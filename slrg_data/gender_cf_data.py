import sys
import getopt

if __name__ == '__main__':
    import collection
    from help_text import COLLECT_CODEFORCES as HELP_TEXT
else:
    from . import collection
    from .help_text import COLLECT_CODEFORCES as HELP_TEXT

try:
    sys.path.append(collection.common.SLRG_DIR)
    import config  # nopep8, pylint: disable=import-error
except ModuleNotFoundError:
    print('Config Error: Could not find config.py.',
          'Please make sure you have run slrg-install.')
    sys.exit()


def _entry():
    _script(sys.argv[1:])


def _script(argv):
    # Declare variables
    users_file = None
    gender_table = None
    gender_file = None
    missing_file = None
    db_login = None
    db_passwd = None

    # Parse command line arguments
    try:
        opts, files = getopt.getopt(argv, "t:o:m:u:p")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-t':
            gender_table = arg
        if opt == '-o':
            gender_file = arg
        elif opt == '-m':
            missing_file = arg
        elif opt == '-u':
            db_login = arg
        elif opt == '-p':
            db_passwd = arg
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

    if users_file is None:
        users_file = input("Codeforces users file: ")
    user_list = collection.common.get_json_data(users_file)

    database = collection.script.make_database(
        config.database, login=db_login, passwd=db_passwd)

    gender_table = collection.script.null_arg_str(
        gender_table, config.tables['gender'], "Gender Table")

    if gender_file is not None:
        gender_file = 'gendered.data'

    if missing_file is None:
        missing_file = 'missing_gender.data'

    _add_gender(user_list, database, gender_table, gender_file, missing_file)


def _add_gender(user_list, database, gender_table, gender_file, miss_file):
    gender = []
    missing = []

    def f(x):
        return collection.codeforces.add_gender(x, database, gender_table)

    for user in map(f, filter(_has_first_name, user_list)):
        if _has_gender(user):
            gender.append(user)
        elif _missing_gender(user):
            missing.append(user)

    collection.common.write_json_data(gender, gender_file)
    collection.common.write_json_data(missing, miss_file)


def _has_first_name(user_data):
    return 'first_name' in user_data and user_data['first_name'] != ''


def _has_gender(user_data):
    return user_data['gender'] == 'male' or user_data['gender'] == 'female'


def _missing_gender(user_data):
    return _has_first_name(user_data) and user_data['gender'] is None


if __name__ == "__main__":
    _entry()
