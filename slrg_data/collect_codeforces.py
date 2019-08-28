"""Collects source code from codeforces submissions.

Usage
=====

Run::

    $ slrg-codeforces [-h] [-i <input data file>] [-s <start index>]
        [-c <number of records to process>] [-u <database username>]
        [-p <database password>]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the value in the config file is None the user will be asked to
input values.

**-h**
    Print out help text.

**-i <input data file>**
    The file containing a list of codeforces user records.
    Default is to ask for it.

**-s <start index>**
    The record to start processing first.

**-c <records to process>**
    The number of records to process in total.

**-u <database username>**
    The database username.

**-p <database password>**
    The database password.
"""
# Standard python modules
import sys
import os
import getopt

# Local imports
from . import collection
from .help_text import COLLECT_CODEFORCES as HELP_TEXT

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
    # Declare variables
    file = None
    start = None
    count = None
    db_login = None
    db_passwd = None

    # Parse command line arguments
    try:
        opts, _ = getopt.getopt(argv, "i:s:c:u:p:h")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-i':
            file = arg
        elif opt == '-s':
            start = arg
        elif opt == '-c':
            count = arg
        elif opt == '-u':
            db_login = arg
        elif opt == '-p':
            db_passwd = arg
        elif opt == '-h':
            print(HELP_TEXT)
            return

    main(file=file, start=start, count=count, db_login=db_login,
         db_passwd=db_passwd)


def main(file=None, start=None, count=None, db_login=None, db_passwd=None):
    """Collects source code from codeforces submissions.

    Args:
        file (str): The name of the file containing user records.
        start (int): The index of the first user record to process.
        count (int): The max number of users to process.
        db_login (str): The username for the database.
        db_passwd (str): The password for the database.

    Returns:
        int: The index of the next user to process in the file of user
            records.
    """
    try:
        script_name = 'codeforces'

        database = collection.script.make_database(config.database,
                                                   login=db_login,
                                                   passwd=db_passwd)

        limits = collection.script.make_cf_limits(
            start, count, config.limits[script_name])
        info = collection.script.make_cf_info(
            file, limits, script_name, config.config)

        log_dir = os.path.join(collection.common.SLRG_DIR, 'codeforces/logs')
        log = collection.common.Log(log_dir, script_name)
        collection.script.remove_old_logs(log_dir, config.max_logs_to_keep)

        collector = collection.codeforces.CfSeleniumCollector(
            database, info, log)
        collector.main()

    except collection.script.ScriptInputError as err:
        print('\n***', err)
