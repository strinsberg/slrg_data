"""Script to collect source code from Ghtorrent records of git projects.

Useable with the records collected with the git_projects.sql(link) from Google
BigQuery and Ghtorrent.

Usage
-----
Run as a command line script in the slrg_data_collection folder.

::

    $ python3 collect_git_projects.py [-h] [-l <programming language>]
        [-i <input data file>] [-s <start index>]
        [-c <records to process>] [-d <database username>]
        [-p <database password>] [--git=<github username>]
        [--gitpass=<github password>]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the config file is None the user will be asked to input values.

**-h**
    Print out help text.

**-l <programming language>**
    The programming language that source is being collected from.
    Determines the table to use and the file extensions. See config.py
    for more info.
    * Default is to ask for it.

**-i <input data file>**
    The data file to process. Can be a filepath relative to the current
    directory or a file name in the data/git_projects directory.
    * Default is to ask for it.

**-s <start index>**
    The entry to start processing first.

**-c <records to process>**
    The count for number of records to process in total.

**-d <database username>**
    Database username.

**-p <database password>**
    The database password.

**--git=<github username>**
    The username of the github account to use with API calls.

**--gitpass=<github password>**
    The password for the github account.

**Note**
    If passwords are given they will be stored during the script's
    execution in plain text. If not given or stored in the config file
    the python module getpass is used to pass them directly into the
    objects which need them: requests and pymysql. If you are concerned
    about how they might handle your passwords consult their
    documentation.
"""
import json
import getopt
import sys
import os

# Had to use the relative imports for sphinx to work properly
# with automodule. It is a little gross, but necessary for now.
try:
    from . import collection
    from . import config
except (ImportError, AttributeError):
    import collection
    import config
    # Gets an attribute error for collection.script.function()
    # if I don't include this even though I did not change the
    # useage to script.function()
    from collection import script


def main(argv):
    """Collect source code from GitHub projects.

    See module documentation for details.

    Args:
        argv (list of str): List of command line arguments an options.
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
        opts, _ = getopt.getopt(argv, "l:i:s:c:d:p:h", ['git=', 'gitpass='])
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
        elif opt == '-d':
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

    # Create objects for collection
    script_name = 'git_projects'

    database = collection.script.make_database(
        config.database, login=db_login, passwd=db_passwd)
    info = collection.script.make_git_info(lang, file, git_login, git_passwd,
                                           script_name, config.tables,
                                           config.git_acct, config.extensions,
                                           config.exclude)
    limits = collection.script.make_limits(
        script_name, config.limits, start, count)
    log = collection.common.Log(os.path.join('logs', script_name), script_name)

    # Create and run collector
    collector = collection.github.ProjectsCollector(
        database, info, limits, log)
    collector.main()


HELP_TEXT = """
$ python3 collect_git_projects.py [-h] [-l < programming language > ]
    [-i < input data file > ] [-s < start index > ] [-c < records to process > ]
    [-d < database username >] [-p < database password > ]
    [--git = <github username >] [--gitpass = <github password > ]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the config file is None the user will be asked to input values.

-h
    Print out help text.

-l < programming language >
    The programming language that source is being collected from.
    Determines the table to use and the file extensions. See config.py
    for more info.
    * Default is to ask for it.

-i < input data file >
    The data file to process. Can be a filepath relative to the current
    directory or a file name in the data/git_projects directory.
    * Default is to ask for it.

-s < start index >
    The entry to start processing first.

-c < records to process >
    The count for number records to process in total.

-d < database username >
    Database username.

-p < database password >
    The database password.

--git = <github username >
    The username of the github account to use with API calls.

--gitpass = <github password >
    The password for the github account.
"""

if __name__ == '__main__':
    main(sys.argv[1:])
