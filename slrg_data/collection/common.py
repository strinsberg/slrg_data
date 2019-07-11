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

# Path to the slrg directory in the users home folder
SLRG_DIR = os.path.join(os.path.expanduser('~'), 'slrg')


# Classes ##############################################################

class Collector:
    """Abstract Class for collecting source code.

    process must be overridden.

    Attributes:
        database (Database): The database to store source code and
            associated information in.
        collection_info (CollectionInfo): Information needed to collect
            source code from a particular source.
        log (Log): A log to send info and errors to.
        times (dict): Times related to the running of the script.
            'start' is the time the script was started.
        totals (dict): Totals for processed data. 'entry' is the total
            number of records processed during the running of
            the script.
        idx (int): The current index in the list of records.
    """

    def __init__(self, database, collection_info, log):
        self.database = database
        self.collection_info = collection_info
        self.log = log
        self.times = {'start': time.time()}
        self.totals = {'entry': 0}
        self.idx = self.collection_info.limits.start

    def main(self):
        """Starts and runs the source collection.

        Returns:
            int: The index of the next record to process in the data
            file.

        Raises:
            DatabaseError
        """
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
        """Does any setup that must happen before the data collection
        starts."""
        self.database.connect()

    def process_data(self, data):
        """Processes each record in the given list of records within the
        limits in the collectio_info attribute.

        Args:
            data (list): A list of dict records to process.
        """
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
        """Processes a record and information and source code from it
        to the database.

        **Must be overridden.**
        """
        assert False, "Collector.process must be overridden"

    def get_entry_values(self, entry):
        """Gets values from an entry and returns them in a list.

        Uses the fields in collection info to collect the values in
        the correct order so they can be added to the database. Also,
        transforms any values that must be transformed before being
        added to the database.

        Args:
            entry (dict): A record being processed.

        Returns:
            list: A list of the values in the order of the fields
            list in collection_info.
        """
        values = []
        for field in self.collection_info.records.fields:
            value = entry[field] if field in entry else None
            values.append(self.transform_entry_value(value, field))

        return values

    def transform_entry_value(self, value, entry_field):
        """Transform a value from a field if needed.

        Default is to return the value unchanged. Should be overridden
        if certain entry fields need to have values transformed.
        """
        return value

    def clean_up(self):
        """Runs any operations that need to be done after the collection
        has finished.

        Will be called even if the script exits due to an error.
        """
        self.database.close()

        self.log.info('------------------------------------------------------')
        self.log.info('Elapsed time: {}'.format(
            find_time(time.time() - self.times['start'])))
        self.log.info('Start={}, Count={}'.format(
            self.collection_info.limits.start, self.collection_info.limits.count))
        self.log.info('Total Entries Processed: {}'.format(
            self.totals['entry']))


class Database:
    """Wrapper for a database.

    Attributes:
        host (str): The database host.
        user (str): The database username.
        name (str): The name of the database.
        passwd (str): The password of the database user. Default is
            None. If None the user will be asked to input it when
            connecting to the datbase and will not be saved by the
            Database class.
    """

    def __init__(self, host, user, name, passwd=None):
        self.host = host
        self.user = user
        self.name = name
        self.passwd = passwd
        self.database = None

    def connect(self, _format=None):
        """Connect to the database.

        Args:
            format (str): The format of the records to be returned.
                'j' for dict results, otherwise tuples will be used.

        Raises:
            script.ScriptInputError: If the database credentials are
            invalid.
        """
        if self.user is None:
            self.user = input("Databse username: ")
        if self.passwd is None:
            passwd = getpass.getpass(prompt="Database Password: ")
        else:
            passwd = self.passwd

        cursor = pymysql.cursors.Cursor
        if _format == 'j':
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
        """Inserts given values into the columns of a given table.

        This is a helper for basic SQL INSERT queries. The values will
        be inserted in order into the columns of the given table.

        Args:
            columns (list): A list of column names. In the order the
                values will be inserted.
            table (str): The name of the table to insert into.
            values (list): A list of values to insert into the table.
                Should be in the same order as the columns list.

        Raises:
            DatabaseError: If there is a problem with the INSERT.
        """
        try:
            sql = "INSERT INTO {} ({}) VALUES({});".format(
                table, ", ".join(columns), self._vals(len(columns)))

            with self.database.cursor() as cursor:
                cursor.execute(sql, values)
            self.database.commit()

        except pymysql.err.MySQLError as error:
            if self.database.open:
                self.database.rollback()
            raise DatabaseError(str(error))

    def select(self, columns, table, where):
        """Selects values from the given columns from the given table.

        This is a helper for basic SQL SELECT queries. The values of
        the given columns will be selected and returned. All where
        clauses will be connected with AND.

        Args:
            columns (list): The column names to select.
            table (str): The table to select from.
            where (list): A list of WHERE clauses. Ie) handle='steve'
                or gender is not null

        Returns:
            list: A list of results in a dict or tuple depending on the
            format passed to Database.connect. Default is tuple.

        Raises:
            DatabaseError: If there is a problem with the SELECT.
        """
        try:
            sep = ", "
            sql = "SELECT {} FROM {} WHERE {};".format(sep.join(columns),
                                                       table, sep.join(where))

            with self.database.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
            return results

        except pymysql.err.MySQLError as error:
            raise DatabaseError(str(error))

    def query(self, sql):
        """Run an SQL query on the database and return the results.

        Should only be used with select queries.

        Args:
            sql (str): A full SQL query for SELECT.

        Returns:
            list: A list of the query results.

        Raises:
            DatabaseError: If there is a problem with the query or if
                certain statements other than select are used.
        """
        not_allowed = ['drop', 'alter', 'update', 'delete', 'insert']
        for stmt in not_allowed:
            if sql.lower().find(stmt) > -1:
                raise DatabaseError(
                    "Database Error: Cannot use "
                    + stmt.upper() + " Database.query")

        try:
            with self.database.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

        except pymysql.err.MySQLError as error:
            raise DatabaseError(str(error))

    def close(self):
        """Closes the database connection."""
        if self.database is not None:
            self.database.close()

    # Helper for insert that creates a string of the right number of %s
    # to be used in the format string passed to cursor.execute.
    def _vals(self, n):
        v = ["%s" for i in range(n)]
        return ", ".join(v)


class Log:
    """Wrapper for logging."""

    def __init__(self, dir_path, file_prefix="log"):
        """Sets up logging to a file in a given directory.

        Args:
            dir_path (str): A path to the directory to store the log
                file in.
            file_prefix (str): All logs will be given unique names based
                on time. The prefix is added to identify what the log
                is for. Default is 'log'.
        """
        path = '{}/{}_{}.log'.format(dir_path, file_prefix, time.time())
        logging.basicConfig(
            filename=path,
            level=logging.INFO,
            format=' %(asctime)s - %(levelname)s - %(message)s')

    def error(self, message, error, critical=False):
        """Logs a message and error.

        Args:
            message (str): A message to include with the error text.
            error (Exception): an Exception object.
            critical (bool): If true then sys.exit is called to end the
                the program.

        Raises:
            sys.exit: If critical is True.
        """
        print('*** Error ***', message + ':', error)
        logging.error('%s: %s', message, str(error))
        if critical:
            sys.exit()

    def info(self, message):
        """Logs a given message."""
        print(message)
        logging.info(message)


# Collection Info and Data Classes #####################################

class CollectionInfo:
    """Collection of different pieces of information needed by
    Collectors.

    Attributes:
        records (RecordsData): Information about the records to be
            processed.
        table (TableData): Information about the table to store data in.
        validation (ValidationData): Information for validating records
            and results during processing.
        limits (LimitData): Information on processing limits.
    """

    def __init__(self, records, table, validation, limits):
        self.records = records
        self.table = table
        self.validation = validation
        self.limits = limits


class RecordsData:
    """Information on the records for processing.

    Attributes:
        filename (str): The filename of the list of records.
        fields (list): The fields that are being stored in the database
            with the source code. Should be in the same order as the
            table columns.
    """

    def __init__(self, filename, fields):
        self.filename = filename
        self.fields = fields


class TableData:
    """Information on the table for storing source code.

    Attributes:
        name (str): The name of the table.
        columns (list): The column names.
    """

    def __init__(self, name, columns):
        self.name = name
        self.columns = columns


class ValidationData:
    """Information for validating records and source code files.

    Attributes:
        extensions (list): List of extensions that are valid.
        exclude_files (list): List of filenames that should not be
            collected.
        exclude_dirs (list): List of directory names that should not
            have their contents collected.
    """

    def __init__(self, extensions, exclude_files, exclude_dirs):
        self.extensions = extensions
        self.exclude_files = exclude_files
        self.exclude_dirs = exclude_dirs


class LimitData:
    """Information on the processing limits of collection.

    Attributes:
        start (int): The first record in a list to process.
        count (int): The max number of records to process.
    """

    def __init__(self, start, count):
        self.start = start
        self.count = count

    def end(self):
        """Returns start + count."""
        return self.start + self.count


class LanguageData:
    """Information on the languages to collect and exclude.

    Attributes:
        collect (list): A list of languages to collect source in.
        exclude (list): A list of languages to exclude from collection.
    """

    def __init__(self, collect, exclude):
        self.collect = collect
        self.exclude = exclude


# Functions ############################################################

def find_time(sec):
    """Finds the time represented by a given number of seconds.

    Args:
        sec (int): The number of seconds.

    Returns:
        str: A string of the time passed. Ie) 10h40m20.00s
    """
    minutes, seconds = (sec / 60, sec % 60)
    hours, minutes = (minutes / 60, minutes % 60)
    return "{:.0f}h{:.0f}m{:.2f}s".format(hours, minutes, seconds)


def get_time_string(timestamp):
    """Converts a timestamp into a string 'dd/mm/yyyy h:m:s'."""
    stamp = int(timestamp)
    date = datetime.fromtimestamp(stamp)
    return date.strftime("%d/%m/%Y %H:%M:%S")


def requests_session(username=None, passwd=None, prompt="Password: "):
    """Create a requests session with optional authentication.

    If username is given then the session will be authenticated with the
    given password or it will ask the user to input one. giving a
    password without a username will return an un-authenticated session.

    Args:
        username (str): The username for the session.
        passwd (str): The passwd for the session.
        prompt (str): The prompt to use when asking for a password if
            one was not given.

    Returns:
        requests.Session: The requests session.
    """
    session = requests.Session()
    if username is not None:
        if passwd is not None:
            session.auth = (username, passwd)
        else:
            session.auth = (username, getpass.getpass(prompt=prompt))
    return session


def session_get_json(session, url):
    """Wraps requests session get call to the given url.

    Catches json.decoder.JSONDecodeError if the result of the get is not
    valid JSON.

    Args:
        session (requests.Session): The request session.
        url (str): The url to GET from.

    Returns:
        dict: The JSON returned by the GET call, or None if there is
            a decoding error.
    """
    for _ in range(10):
        try:
            return session.get(url).json()
        except json.decoder.JSONDecodeError:
            return None
        except requests.exceptions.ConnectionError as err:
            time.sleep(30)
            print("Connection Error:", str(err))


def get_json_data(path):
    """Loads JSON data from a given path and returns it."""
    with open(path) as file:
        return json.load(file)


def write_json_data(path, data):
    """Writes JSON data to a given path."""
    with open(path, 'w') as file:
        json.dump(data, file)


def get_gender(name, database, table, write=lambda x: None):
    """Collects the gender of a name from the given database or the
    genderize.io API.

    Args:
        name (str): The name to find gender for.
        database (Database): A database to search for the name before
            the API.
        table (str): The name of the table that gender information is
            stored in.
        write (str): A function to send information text to. Defaults
            to one that does nothing.

    Returns:
        tuple: A tuple with (gender, gender probability). If the
        name is not in the database and the API limit is exceeded.

    Raises:
        AssertionError: If the name is None or the empty string.
    """
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
    """Retrive gender for a name from the given database and table.

    Args:
        name (str): The name to find gender for.
        database (Database): A database to search.
        table (str): The name of the table that gender information is
            stored in.

    Returns:
        tuple: A tuple with (gender, gender probability) if the name is
        found, otherwise None.
    """
    columns = ['gender', 'probability']

    if name.find('"') > -1:
        return None

    where = ['name="{}"'.format(name)]
    result = database.select(columns, table, where)
    if result is not None and result:
        return result[0]
    return None


def get_gender_from_api(name):
    """Retreive the gender of a name from the genderize.io API.

    Args:
        name (str): The name to find gender for.

    Returns:
        tuple: A tuple with (gender, gender probability). if gender is
        unknown it will return ('nil', 0.0). If API limit is exceeded
        it will return (None, None).
    """
    url = "https://api.genderize.io/?name=" + name
    # If the connection has problems sleep and try again. Max 10 tries.
    for _ in range(10):
        try:
            r = requests.get(url)
            data = r.json()
            break
        except json.decoder.JSONDecodeError:
            data = {'error': True}
            break
        except requests.exceptions.ConnectionError as err:
            time.sleep(30)
            print("Connection Error:", str(err))

    if 'error' in data:
        return (None, None)
    if data['gender']:
        return [data['gender'], float(data['probability'])]
    return ['nil', 0.0]


def update_gender_table(name, gender_info, database, table):
    """Insert a names gender info in a database table.

    Args:
        name (str): The name to find gender for.
        gender_info (tuple): The gender info as (gender, probability)
        database (Database): A database to search.
        table (str): The name of the table that gender information is
            stored in.
    """
    columns = ['name', 'gender', 'probability']
    values = [name]
    values.extend(gender_info)
    database.insert(columns, table, values)


# Exceptions ###########################################################

class DatabaseError(Exception):
    """Exceptions that occur during database operations."""
