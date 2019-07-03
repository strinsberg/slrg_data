"""Script to run a SELECT query on a database and get the results as
a CSV or JSON file.

Usage
=====
Run as a command line script in the slrg_data_collection folder

::

    $ python3 select.py [-h] [-j | -c] [-o <output file>] [-i <input sql file>]
        [-u <database username>] [-p <database password>]

Options
~~~~~~~

**-h**
    Print help text.

**-j | -c**
    Output in JSON or CSV format. If both are given the first
    will be used.

**-o <output file>**
    The file to write the results to. If a path is given it must be
    relative to the slrg_data_collection directory.

**-i <input sql file>**
    A file with the SQL SELECT query. If a path is given it must be
    relative to the slrg_data_collection directory.

**-u <database username>**
    The database username. Defaults to value in config file, if it is
    None value will be asked for.

**-p <database password>**
    The database password. Defaults to value in config file. If config
    value is None it will be asked for.
"""
import getopt
import sys
import os
import json
import csv

if __name__ == '__main__':
    import collection
    from help_text import SELECT as HELP_TEXT
else:
    from . import collection
    from .help_text import SELECT as HELP_TEXT

sys.path.append(collection.common.SLRG_DIR)
import config  # nopep8


def _get_query(sql_file=None):
    """Get the SQL query from the given file or ask for it.

    If the sql_file is None the user will be asked for an SQL SELECT
    statement.

    Args:
        sql_file (str): A path to a file containing an SQL SELECT
            statement. Default is None.

    Returns:
        str: A string of the SQL to be queried.
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


def _get_file_and_format(file, format_):
    """Get the file path and format type for the results.

    If args are None then the user will be asked for values.

    Args:
        file (str): a file path.
        format_ (str): a 'j' or 'c' representing the desired output
            format in JSON or CSV.

    Returns:
        str, str: The filepath and the letter for the output format.
    """
    if file is None:
        file = input("Output file: ")

    if format_ is None:
        format_ = input("Output JSON(j) or CSV(c): ").lower()

    if format_ not in ['c', 'j']:
        raise collection.script.ScriptInputError(
            "Input error: Not a valid format: " + format_)

    return file, format_


def _script():
    script(sys.argv[1:])


def script(argv):
    # Declare some variables
    output_file = None
    sql_file = None
    output_format = None
    login = None
    passwd = None

    # Parse command line options
    try:
        opts, _ = getopt.getopt(argv, "o:i:u:p:cjh")
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
        elif opt == '-h':
            print(HELP_TEXT)
            return

    main(output_file=output_file, sql_file=sql_file,
         output_format=output_format, db_login=login, db_passwd=passwd)


def main(output_file=None, sql_file=None, output_format=None, db_login=None,
         db_passwd=None):
    """Main for script to SELECT records from a database.

    See module documentation for more details.

    Args:
        argv (list of str): List of command line arguments and options.
    """
    try:
        # Set some variables
        output_file, output_format = _get_file_and_format(output_file,
                                                          output_format)
        sql = _get_query(sql_file)
        # Should validate the query does not contain any unwanted statements
        # put a script in query to take a list of allowed and list of
        # not allowed operations and return true or false to let it through

        if db_login is None:
            db_login = config.database['login']
        if db_passwd is None:
            db_passwd = config.database['passwd']

        # Run the query and print it's message
        database = collection.script.make_database(config.database,
                                                   login=db_login,
                                                   passwd=db_passwd)
        print(collection.query.query_db(
            database, sql, output_file, output_format))

    except collection.script.ScriptInputError as err:
        print("\n***", err)

    except FileNotFoundError as err:
        print('\n*** Input Error: Bad file path', output_file)

    except collection.common.DatabaseError as err:
        print("\n***", err)


if __name__ == '__main__':
    _script()
