"""Common classes and functions to support collecting source code from
the internet.
"""
from datetime import datetime
import time
import sys
import getpass
import json
import logging
import os

# 3rd party modules
import requests
import pymysql

# My modules
from . import script

# Constants ############################################################

SLRG_DIR = os.path.join(os.path.expanduser('~'), '.slrg')

# Classes ##############################################################


class Collector:
    """Abstract Class for collecting information from the internet."""

    def __init__(self, database, collection_info, log):
        self.database = database
        self.collection_info = collection_info
        self.log = log
        self.times = {'start': time.time()}
        self.totals = {'entry': 0}
        self.idx = self.collection_info.limits.start

    def main(self):
        """Runs the extraction."""
        try:
            self.set_up()
            data = get_json_data(self.collection_info.records.filename)
            self.process_data(data)

        except DatabaseError as error:
            self.log.error("Databse error caught in main", error)
            raise DatabaseError(error)

        finally:
            self.clean_up()

        return self.idx + 1

    def set_up(self):
        """Things to run before starting collection."""
        self.database.connect()

    def process_data(self, data):
        """Processes each entry in the data within the desired range."""
        for idx, entry in enumerate(data):
            # Only process records in the desired range
            if idx < self.collection_info.limits.start:
                continue
            elif idx >= self.collection_info.limits.end():
                break

            # Process the entry as a derived class needs
            self.process(entry)

            self.totals['entry'] += 1
            self.idx = idx

    # Override
    def process(self, entry):
        """Process and insert an entry into the database."""
        assert False, "Collector.process must be overridden"

    def get_entry_values(self, entry):
        """Gets a files associated info from an entry to add to database."""
        values = []
        for field in self.collection_info.records.fields:
            value = entry[field] if field in entry else None
            values.append(self.transform_entry_value(value, field))

        return values

    def transform_entry_value(self, value, entry_field):
        return value

    def clean_up(self):
        """Runs desired cleanup code at the end of main."""
        self.database.close()

        self.log.info('------------------------------------------------------')
        self.log.info('Elapsed time: {}'.format(
            find_time(time.time() - self.times['start'])))
        self.log.info('Start={}, Count={}'.format(
            self.collection_info.limits.start, self.collection_info.limits.count))
        self.log.info('Total Entries Processed: {}'.format(
            self.totals['entry']))


class Database:
    """Warpper for a database used by other classes."""

    def __init__(self, host, user, name, passwd=None):
        self.host = host
        self.user = user
        self.name = name
        self.passwd = passwd
        self.database = None

    def connect(self, format_=None):
        """Connect to the database."""
        if self.user is None:
            self.user = input("Databse username: ")
        if self.passwd is None:
            passwd = getpass.getpass(prompt="Database Password: ")
        else:
            passwd = self.passwd

        cursor = pymysql.cursors.Cursor
        if format_ == 'j':
            cursor = pymysql.cursors.DictCursor

        try:
            self.database = pymysql.connect(
                self.host, self.user, passwd, self.name, cursorclass=cursor)
        except pymysql.err.OperationalError as err:
            code, _ = err.args
            if code == 1045:
                raise script.ScriptInputError(
                    'Input Error: Bad database username or password')

    def insert(self, columns, table, values):
        """Simple insert funtion for adding a list of values to a
        table in the database."""
        try:
            sql = "INSERT INTO {} ({}) VALUES({});".format(
                table, ", ".join(columns), self._vals(len(columns)))

            with self.database.cursor() as cursor:
                cursor.execute(sql, values)
            self.database.commit()

        except pymysql.err.MySQLError as error:
            if self.database.open:
                self.database.rollback()
            raise DatabaseError(str(error) + " -- SQL: " + sql)

    def select(self, columns, table, where):
        """Simple select function for querying a table in the database."""
        try:
            sep = ", "
            sql = "SELECT {} FROM {} WHERE {};".format(sep.join(columns),
                                                       table, sep.join(where))

            with self.database.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
            return results

        except pymysql.err.MySQLError as error:
            raise DatabaseError(str(error) + " -- SQL: " + sql)

    def query(self, sql):
        """Run a Query on the database."""
        try:
            with self.database.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

        except pymysql.err.MySQLError as error:
            raise DatabaseError("Database Error: " + str(error))

    def close(self):
        """Close the database connection."""
        if self.database is not None:
            self.database.close()

    # Helper for insert that creates a string of the right number of %s
    # to be used in the format string passed to cursor.execute.
    def _vals(self, n):
        v = ["%s" for i in range(n)]
        return ", ".join(v)


class Log:
    """Wrapper for logging used by other classes."""

    def __init__(self, dir_path, file_prefix="log"):
        path = '{}/{}_{}.log'.format(dir_path, file_prefix, time.time())
        logging.basicConfig(
            filename=path,
            level=logging.INFO,
            format=' %(asctime)s - %(levelname)s - %(message)s')

    def info(self, message):
        print(message)
        logging.info(message)

    def error(self, message, error, critical=False):
        print('*** Error ***', message + ':', error)
        logging.error('%s: %s', message, str(error))
        if critical:
            sys.exit()


class CollectionInfo:
    def __init__(self, records, table, validation, limits):
        self.records = records
        self.table = table
        self.validation = validation
        self.limits = limits


class RecordsData:
    def __init__(self, filename, fields):
        self.filename = filename
        self.fields = fields


class TableData:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns


class ValidationData:
    def __init__(self, extensions, exclude_files, exclude_dirs):
        self.extensions = extensions
        self.exclude_files = exclude_files
        self.exclude_dirs = exclude_dirs


class LimitData:
    def __init__(self, start, count):
        self.start = start
        self.count = count

    def end(self):
        return self.start + self.count


class LanguageData:
    def __init__(self, collect, exclude):
        self.collect = collect
        self.exclude = exclude


# Functions ############################################################


def find_time(sec):
    """Finds hh:mm:ss time from a given number of seconds."""
    minutes, seconds = (sec / 60, sec % 60)
    hours, minutes = (minutes / 60, minutes % 60)
    return "{:.0f}h{:.0f}m{:.2f}s".format(hours, minutes, seconds)


def get_time_string(timestamp):
    """Converts a unix timestamp into a string 'dd/mm/yyyy h:m:s'."""
    stamp = int(timestamp)
    date = datetime.fromtimestamp(stamp)
    return date.strftime("%d/%m/%Y %H:%M:%S")


def requests_session(username=None, passwd=None, prompt="Password: "):
    """Create a requests session with optional authentication."""
    session = requests.Session()
    if username is not None:
        if passwd is not None:
            session.auth = (username, passwd)
        else:
            session.auth = (username, getpass.getpass(prompt=prompt))
    return session


def get_json_data(path):
    """Loads JSON data from a file and returns it."""
    with open(path) as file:
        return json.load(file)


def write_json_data(path, data):
    """Writes JSON data to a file."""
    with open(path, 'w') as file:
        json.dump(data, file)


def get_gender(name, database, table, write=lambda x: None):
    """Collect the gender of a name from the given database or the
    genderize.io api."""
    assert name not in [None, ''], "No name given to get_gender"

    name = name.lower()
    # Need to add a little validation for names containing quotes

    gender_info = get_gender_from_database(name, database, table)
    if gender_info is not None:
        write("-- Found in dataset: " + gender_info[0])
        return (gender_info[0], float(gender_info[1]))

    gender_info = get_gender_from_api(name)
    if gender_info[0] is not None:
        write("-- Found from api: " + gender_info[0])
        update_gender_table(name, gender_info, database, table)
        return (gender_info[0], float(gender_info[1]))
    else:
        return (None, None)


def get_gender_from_database(name, database, table):
    """Retrive gender  for a name from the given database and table."""
    columns = ['gender', 'probability']
    where = ['name=\"{}\"'.format(name)]
    result = database.select(columns, table, where)
    if result is not None and result:
        return result[0]
    return None


def get_gender_from_api(name):
    """Retreive the gender of a name from the genderize.io api."""
    url = "https://api.genderize.io/?name=" + name
    r = requests.get(url)
    data = r.json()

    if 'error' in data:
        return (None, None)

    if data['gender']:
        return [data['gender'], float(data['probability'])]
    else:
        return ['nil', 0.0]


def update_gender_table(name, gender_info, database, table):
    """Insert a names gender info in a database's gender table."""
    columns = ['name', 'gender', 'probability']
    values = [name]
    values.extend(gender_info)
    database.insert(columns, table, values)

# Exceptions ###########################################################


class DatabaseError(Exception):
    """Errors with the database."""
