"""Collects source code from github commits.

Useable with the records collected with the git_projects.sql(link)
from Google BigQuery and Ghtorrent.

Usage
-----

Run::

    $ slrg-git-commits [-h] [-l <programming language>]
        [-i <input data file>] [-s <start index>]
        [-c <records to process>] [-u <database username>]
        [-p <database password>] [--git=<github username>]
        [--gitpass=<github password>]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the value in the config file is None the user will be asked to
input values.

**-h**
    Print out help text.

**-l <programming language>**
    The programming language that source is being collected from.
    Determines the table to use and the file extensions. See config.py
    for more info.
    * Default is to ask for it.

**-i <input data file>**
    The file containing a list of codeforces user records.
    * Default is to ask for it.

**-s <start index>**
    The record to start processing first.

**-c <records to process>**
    The number of records to process in total.

**-u <database username>**
    The database username.

**-p <database password>**
    The database password.

**--git=<github username>**
    The username of the github account to use with API calls.

**--gitpass=<github password>**
    The password for the github account.
"""
# Standard python modules
import os
import sys
import getopt
import json

# Local imports
from . import collection
from .help_text import COLLECT_GIT_PROJECTS as HELP_TEXT

# Add the directory with the configuration file to the path
try:
    sys.path.append(collection.common.SLRG_DIR)
    import config  # nopep8, pylint: disable=import-error
except ModuleNotFoundError:
    print('Config Error: Could not find config.py.',
          'Please make sure you have run slrg-install.')
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
    lang = None
    file = None
    start = None
    count = None
    db_login = None
    db_passwd = None
    git_login = None
    git_passwd = None

    # Parse command line arguments
    try:
        opts, _ = getopt.getopt(argv, "l:i:s:c:u:p:h", ['git=', 'gitpass='])
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-l':
            lang = arg
        elif opt == '-i':
            file = arg
        elif opt == '-s':
            start = arg
        elif opt == '-c':
            count = arg
        elif opt == '-u':
            db_login = arg
        elif opt == '-p':
            db_passwd = arg
        elif opt == '--git':
            git_login = arg
        elif opt == '--gitpass':
            git_passwd = arg
        elif opt == '-h':
            print(HELP_TEXT)
            return

    main(lang=lang, file=file, start=start, count=count, db_login=db_login,
         db_passwd=db_passwd, git_login=git_login, git_passwd=git_passwd)


def main(lang=None, file=None, start=None, count=None, db_login=None,
         db_passwd=None, git_login=None, git_passwd=None):
    """Collects source code from GitHub commits.

    Args:
        lang (str): The programming language to collect source code for.
        file (str): The name of the file containing GitHub commit
            records obtained from Ghtorrent.
        start (int): The index of the first user record to process.
        count (int): The max number of users to process.
        db_login (str): The username for the database.
        db_passwd (str): The password for the database.
        git_login (str): A GitHub username.
        git_passwd (str): The password for the GitHub username.

    Returns:
        int: The index of the next project to process from the file of
            Ghtorrent commit records.
    """
    try:
        # Create objects for collection
        script_name = 'git_commits'

        database = collection.script.make_database(config.database,
                                                   login=db_login,
                                                   passwd=db_passwd)
        limits = collection.script.make_limits(
            start, count, config.limits[script_name])
        git_data = collection.script.make_git_data(git_login, git_passwd,
                                                   config.git_acct)
        info = collection.script.make_git_info(lang, file, git_data, limits,
                                               script_name, config.config)

        log_dir = os.path.join(collection.common.SLRG_DIR, 'logs', script_name)
        log = collection.common.Log(log_dir, script_name)
        collection.script.remove_old_logs(log_dir, config.max_logs_to_keep)

        # Create and run collector
        collector = collection.github.CommitsCollector(
            database, info, log, lang)
        return collector.main()

    except collection.script.ScriptInputError as err:
        print('\n***', err)
