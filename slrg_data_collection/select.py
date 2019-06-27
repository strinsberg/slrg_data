# script to make an sql query on the database

import getopt
import sys
import os
import json
import csv
import config
from collection import query
from collection import script
from collection import common


def _get_query(query_file):
    if query_file is None:
        query = input("Sql SELECT statement: ")
    else:
        if not os.path.isfile(query_file):
            query_file = os.path.join('sql', query_file)
        with open(query_file) as file:
            query = file.read()
            query = query.replace('\n', ' ')
    return query


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
    query_file = None
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
            query_file = arg
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
    query = _get_query(query_file)
    # Should validate the query does not contain any unwanted statements
    # put a script in query to take a list of allowed and list of
    # not allowed operations and return true or false to let it through

    if login is None:
        login = config.database['login']
    if passwd is None:
        passwd = config.database['passwd']

    # Run the query and print the result
    database = script.make_database(
        config.database, login=login, passwd=passwd)
    print(query.query_db(database, query, output_format))


HELP_TEXT = "Unfinished"

if __name__ == '__main__':
    main(sys.argv[1:])
