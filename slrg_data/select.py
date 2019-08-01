"""Script to run a SELECT query on a database and get the results as
a CSV or JSON file.

Can be run as a command line script or imported as a module and run with
select.main().

Usage
=====
As a command line script.

Run::

    $ slrg-select [-h] [-j | -c] [-n] [-o <output file>]
        [-i <input sql file>] [-u <database username>]
        [-p <database password>]

Options
~~~~~~~

**-h**
    Print help text.

**-j | -c**
    Output in JSON or CSV format. If both are given the first
    will be used.

**-n**
    if Selected a header row will be printed at the top of the csv with
    column names used in select statement. Only applicable to **CSV**
    output.

**-o <output file>**
    The file to write the results to.

**-i <input sql file>**
    A file with the SQL SELECT query. If not given an SQL
    Select statement will be asked for.

**-u <database username>**
    The database username. Defaults to value in config file, if config
    value is None it will be asked for.

**-p <database password>**
    The database password. Defaults to value in config file. If config
    value is None it will be asked for.
"""
# Standar modules
import getopt
import sys
import os
import json
import csv

# Local imports
from . import collection
from .help_text import SELECT as HELP_TEXT

# Add the directory with the configuration file to the path
try:
    sys.path.append(collection.common.SLRG_DIR)
    import config  # nopep8, pylint: disable=import-error
except ModuleNotFoundError:
    print('Config Error: Could not find config.py.',
          'Try re-installing the slrg_data package.',
          'If this does not work consult the config section of the documentation.')
    sys.exit()


# Script and Main Functions ############################################

def _entry():
    """Entry point for the script."""
    _script(sys.argv[1:])


def _script(argv):
    """Processes command line arguments and calls main with their values.

    See module details for more info on command line options.

    Args:
        argv (list of str): The list of command line options and args
            not containing the script name.
    """
    # Declare some variables
    output_file = None
    sql_file = None
    output_format = None
    login = None
    passwd = None
    names = False

    # Parse command line options
    try:
        opts, _ = getopt.getopt(argv, "o:i:u:p:cjhn")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-o':
            output_file = arg
        elif opt == '-i':
            sql_file = arg
        elif opt in ['-c', '-j']:
            if output_format is None:
                output_format = opt[1]
        elif opt == '-u':
            login = arg
        elif opt == '-p':
            passwd = arg
        elif opt == '-n':
            names = True
        elif opt == '-h':
            print(HELP_TEXT)
            return

    main(output_file=output_file, sql_file=sql_file,
         output_format=output_format, db_login=login, db_passwd=passwd, names=names)


def main(output_file=None, sql_file=None, output_format=None, db_login=None,
         db_passwd=None, names=False):
    """Collects results of an sql SELECT query and writes the results to
    a JSON or CSV file.

    All args defualt to None. If they are left as None the configuration
    file will be consulted and if a value cannot be found then the user
    will be prompted for one.

    Args:
        output_file (str): Name of the file to write the results to.
        sql_file (str): Name of sql to run. If left as none the user
            will be asked for an SQL query.
        output_format (str): j for JSON or c for CSV.
        db_login (str): The username for logging onto the database.
        db_password (str): The database users password.
        names (bool): Wether to add a row with column names at the top
            of a CSV file.
    """
    try:
        # Set some variables
        output_file, output_format = _get_file_and_format(output_file,
                                                          output_format)
        sql = _get_query(sql_file)

        if db_login is None:
            db_login = config.database['login']
        if db_passwd is None:
            db_passwd = config.database['passwd']

        # Run the query and print it's message
        database = collection.script.make_database(config.database,
                                                   login=db_login,
                                                   passwd=db_passwd)
        print(_query_and_output(database, sql, output_file, output_format, names))

    except collection.script.ScriptInputError as err:
        print("\n***", err)

    except FileNotFoundError as err:
        print('\n*** Input Error: Bad file path', output_file)

    except collection.common.DatabaseError as err:
        print("\n***", err)


# Helper Functions #####################################################

def _get_file_and_format(file, format_):
    """Get the file path and format type for the results.

    If args are None then the user will be asked for values.

    Args:
        file (str): a file path.
        format_ (str): a 'j' or 'c' representing the desired output
            format in JSON or CSV.

    Returns:
        str, str: The filepath and the letter for the output format.

    Raises:
        collection.script.ScriptInputError
    """
    if file is None:
        file = input("Output file: ")

    if format_ is None:
        format_ = input("Output JSON(j) or CSV(c): ").lower()

    if format_ not in ['c', 'j']:
        raise collection.script.ScriptInputError(
            "Input error: Not a valid format: " + format_)

    return file, format_


def _get_query(sql_file=None):
    """Get the SQL query from the given file or ask for it.

    If the sql_file is None the user will be asked for an SQL SELECT
    statement.

    Args:
        sql_file (str): A path to a file containing an SQL SELECT
            statement. Default is None.

    Returns:
        str: A string of the SQL to be queried.

    Raises:
        collection.script.ScriptInputError
    """
    try:
        if sql_file is None:
            sql = input("Sql SELECT statement: ")
        else:
            if not os.path.isfile(sql_file):
                sql_file = os.path.join('sql', sql_file)
            with open(sql_file) as file:
                sql = file.read()
                sql = sql.replace('\n', ' ')
        return sql

    except FileNotFoundError:
        raise collection.script.ScriptInputError(
            "Input Error: No Sql file: " + sql_file)


def _query_and_output(database, sql, out_file, _format, names=False):
    """Queries the database and writes the results to a file.

    Writes results to the file in the given _format.

    Args:
        database (common.Database): A database object
        sql (str): The query to run. Should be a SELECT query only.
        _format (str): j for JSON output or c for CSV output.
        names (bool): Weather or not to place column names in the first
            row of a CSV

    Returns
        str: A message about the success or failure of the query and
            file output.
    """
    try:
        database.connect(_format='j')
        results = database.query(sql)

        if _format == 'j':
            with open(out_file, 'w') as file:
                json.dump(results, file)

        elif _format == 'c':
            header = []
            if results:
                header = [x for x in results[0]]

            new_results = []
            for result in results:
                row = [result[h] for h in header]
                new_results.append(row)
            results = new_results

            with open(out_file, 'w', newline='') as csvfile:
                wr = csv.writer(csvfile, delimiter=',')
                if names:
                    wr.writerow(header)
                wr.writerows(results)

        return "Successfully wrote to " + out_file

    except collection.common.DatabaseError as error:
        raise collection.common.DatabaseError(str(error))

    finally:
        database.close()


# Run ##################################################################

if __name__ == '__main__':
    _entry()
