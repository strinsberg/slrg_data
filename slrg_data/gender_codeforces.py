"""Adds gender to all codeforces users it can and writes their records
to a new file.

The records that have a gender are written to a new file. The records
that are not able to be labeled, if the api is down, are written to
another file to be processed later.

Usage
=====

Run::

    $ slrg-gender-codeforces [-h] [-i <codeforces users file>]
        [-o <output file>] [-m <missing gender file>]
        [-t <gender table name>] [-u <databse username>]
        [-p <database password>]

Options
~~~~~~~

**-h**
    Print help text.

**-i <codeforces user file>**
    The file containing a list of codeforces user records. If left blank
    it will be prompted for.

**-o <output file>**
    The file to write the gendered results to.
    Default is gendered.data

**-m <missing gender file>**
    The file to write records that cannot be gendered yet because
    the gender API is unavailable.
    Default is missing_gender.data

**-t <gender table name>**
    The name of the gender table in the database.
    Defaults to value in config file. If the value in config is None
    it will be asked for.

**-u <database username>**
    The database username.
    Defaults to value in config file. If the value in config is None
    it will be asked for.

**-p <database password>**
    The database password.
    Defaults to value in config file. If the value in config is None
    it will be asked for.
"""
# Standard python modules
import sys
import getopt

# Local imports
from . import collection
from .help_text import GENDER_CODEFORCES as HELP_TEXT

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
    """Script entry point."""
    _script(sys.argv[1:])


def _script(argv):
    """Processes command line arguments and calls main with their values.

    See module details for more info on command line options.

    Args:
        argv (list of str): The list of command line options and args
            not containing the script name.
    """
    # Declare variables
    users_file = None
    gender_table = None
    gender_file = None
    missing_file = None
    db_login = None
    db_passwd = None

    # Parse command line arguments
    try:
        opts, _ = getopt.getopt(argv, "m:i:t:o:u:p:h")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-t':
            gender_table = arg
        elif opt == '-i':
            users_file = arg
        elif opt == '-o':
            gender_file = arg
        elif opt == '-m':
            missing_file = arg
        elif opt == '-u':
            db_login = arg
        elif opt == '-p':
            db_passwd = arg
        elif opt == '-h':
            print(HELP_TEXT)
        else:
            print("Unkown option:", opt)
            print(HELP_TEXT)
            sys.exit()

    main(users_file=users_file, db_login=db_login, db_passwd=db_passwd,
         gender_table=gender_table, gender_file=gender_file,
         missing_file=missing_file)


def main(users_file=None, db_login=None, db_passwd=None,
         gender_table=None, gender_file=None, missing_file=None):
    """Adds gender to all users in a codeforces user list and writes
    those with gender to a new file.

    Also writes those that cannot have gender found yet to another file
    for processing later.

    Args:
        users_file (str): The name of the Codeforces user file. If it is
            None then the user will be prompted for it.
        db_login (str): The username for the database. If it is None
            the user will be prompted for it.
        db_passwd (str): The password for the database. If it is None
            the user will be prompted for it.
        gender_table (str): The name of the table where gender data
            is stored in the database.
        gender_file (str): File to write the results that have a gender.
            If it is None it will be 'gendered.data'.
        missing_file (str): File to write the results that could not
            be gendered yet. Most likely because the gender API rate
            limit was reached. If it is None it will be
            'missing_gender.data'.
    """
    if users_file is None:
        users_file = input("Codeforces users file: ")
    user_list = collection.common.get_json_data(users_file)

    database = collection.script.make_database(
        config.database, login=db_login, passwd=db_passwd)

    gender_table = collection.script.null_arg_str(
        gender_table, config.tables['gender'], "Gender Table")

    if gender_file is None:
        gender_file = 'gendered.data'

    if missing_file is None:
        missing_file = 'missing_gender.data'

    try:
        database.connect()
        _add_gender(user_list, database, gender_table,
                    gender_file, missing_file)

    except collection.script.ScriptInputError as err:
        print('\n***', err)

    finally:
        database.close()


# Helpers ##############################################################

def _add_gender(user_list, database, gender_table, gender_file, miss_file):
    """Does the actual work of filtering the user list and writing the
    new lists to files.

    Args:
        user_list (str): A list of codeforces user records.
        out_file (str): The name of the file to write the results to.
        db_login (str): The username for the database.
        db_passwd (str): The password for the database.
        gender_table (str): The name of the table where gender data
            is stored in the database.
        gender_file (str): File to write the results that have a gender.
        missing_file (str): File to write the results that could not
            be gendered yet. Most likely because the gender API rate
            limit was reached.
    """
    gendered = []
    missing = []

    gender_collector = collection.common.GenderCollector(
        database, gender_table)

    try:
        for i, user in enumerate(user_list):
            if _has_first_name(user):
                name = user['firstName']

                gender, prob = gender_collector.get_gender(name)
                collection.codeforces.add_gender(user, database, gender_table)

                user['gender'] = gender
                user['gender_probability'] = prob

                print("#", i, " -- First name:",
                      name.split()[0],
                      "**", gender, "**")

                if _has_gender(user):
                    gendered.append(user)
                elif _missing_gender(user):
                    missing.append(user)

    finally:
        collection.common.write_json_data(gender_file, gendered)
        collection.common.write_json_data(miss_file, missing)


def _has_first_name(user_data):
    """Returns True if a codeforces user record has a first name."""
    return 'firstName' in user_data and user_data['firstName'].strip() != ''


def _has_gender(user_data):
    """Returns True if a codeforces user record has a gender."""
    return user_data['gender'] == 'male' or user_data['gender'] == 'female'


def _missing_gender(user_data):
    """Returns True if a codeforces user record has a first name, but
    has not been given a gender.
    """
    return _has_first_name(user_data) and user_data['gender'] is None
