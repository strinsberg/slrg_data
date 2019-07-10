"""Adds gender to all codeforces users it can and writes their records
to a new file.

The records that have a gender are written to a new file. The records
that are not able to be labeled, if the api is down, are written to
another file to be processed later.

Usage
=====

Run::

    $ slrg-gender-codeforces [options]

Options
~~~~~~~


"""
# Standard python modules
import sys
import getopt

# Local imports
if __name__ == '__main__':
    import collection
    from help_text import GENDER_CODEFORCES as HELP_TEXT
else:
    from . import collection
    from .help_text import GENDER_CODEFORCES as HELP_TEXT

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
        opts, files = getopt.getopt(argv, "t:o:m:u:p:h")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-t':
            gender_table = arg
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

    if files:
        users_file = files[0]

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
        etc.
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
    finally:
        database.close()


# Helpers ##############################################################

def _add_gender(user_list, database, gender_table, gender_file, miss_file):
    """Does the actual work of filtering the user list and writing the
    new lists to files.

    Args:
        etc.
    """
    gender = []
    missing = []

    try:
        for i, user in enumerate(user_list):
            if _has_first_name(user):
                collection.codeforces.add_gender(user, database, gender_table)
                print("#", i, " -- First name:",
                      user['firstName'].split()[0],
                      "**", user['gender'], "**")
                if _has_gender(user):
                    gender.append(user)
                elif _missing_gender(user):
                    missing.append(user)

    finally:
        collection.common.write_json_data(gender_file, gender)
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


# Run ##################################################################

if __name__ == "__main__":
    _entry()
