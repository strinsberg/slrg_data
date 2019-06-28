# script to make an sql query on the database

import getopt
import sys
import os
import json
import csv

if __name__ == '__main__':
    import config
    import collection
else:
    from . import config
    from . import collection


def _get_query(sql_file):
    if sql_file is None:
        sql = input("Sql SELECT statement: ")
    else:
        if not os.path.isfile(sql_file):
            sql_file = os.path.join('sql', sql_file)
        with open(sql_file) as file:
            sql = file.read()
            sql = sql.replace('\n', ' ')
    return sql


def _get_file_and_format(file, format_):
    if file is None:
        file = input("Output file: ")

    if format_ is None:
        format_ = input("Output JSON(j) or CSV(c): ").lower()

    if format_ not in ['c', 'j']:
        print("Invalid format!!")
        sys.exit()

    return file, format_


def main(argv):
    # Declare some variables
    output_file = None
    sql_file = None
    output_format = None
    login = None
    passwd = None

    # Parse command line options
    try:
        opts, _ = getopt.getopt(argv, "o:f:u:p:cjh")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-o':
            output_file = arg
        elif opt == '-f':
            sql_file = arg
        elif opt in ['-c', '-j']:
            output_format = opt[1]
        elif opt == '-u':
            login = arg
        elif opt == '-p':
            passwd = arg
        elif opt == '-h':
            print(HELP_TEXT)
            return

    # Set some variables
    output_file, output_format = _get_file_and_format(
        output_file, output_format)
    sql = _get_query(sql_file)
    # Should validate the query does not contain any unwanted statements
    # put a script in query to take a list of allowed and list of
    # not allowed operations and return true or false to let it through

    if login is None:
        login = config.database['login']
    if passwd is None:
        passwd = config.database['passwd']

    # Run the query and print the result
    database = collection.script.make_database(
        config.database, login=login, passwd=passwd)
    print(collection.query.query_db(database, sql, output_file, output_format))


HELP_TEXT = "Unfinished"

if __name__ == '__main__':
    main(sys.argv[1:])
