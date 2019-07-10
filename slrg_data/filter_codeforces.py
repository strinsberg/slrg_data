"""This will be a script to filter out a certain group of users from
a codeforces users list. Preferably one that has been gendered fully.
It might also be worth processing that list first to find out what all
the first names are that are available and possibly trying a different
method for obtaining gender labels to see what we can get. The
processing may end up being a script and it may end up just being something
I do, and just keep the user data.
"""
import sys
import getopt

if __name__ == '__main__':
    import collection
    from help_text import GENDER_CODEFORCES as HELP_TEXT
else:
    from . import collection
    from .help_text import GENDER_CODEFORCES as HELP_TEXT

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
    out_file = None
    users_file = None
    country = []
    gender = []
    gen_prob = 0.5
    handle = []
    org = []
    rank = []
    rating = 1000

    try:
        opts, file = getopt.getopt(argv, "o:h",
                                   ['country=', 'gender=', 'gen_prob=', 'handle=', 'org=', 'rank=', 'rating='])
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '--country':
            country.extend(_split_and_lower(arg))
        elif opt == '--gender':
            gender.extend(_split_and_lower(arg))
        elif opt == '--gen_prob':
            gen_prob = float(arg)
        elif opt == '--handle':
            handle.extend(_split_and_lower(arg))
        elif opt == '--org':
            org.extend(_split_and_lower(arg))
        elif opt == '--rank':
            rank.extend(_split_and_lower(arg))
        elif opt == '--rating':
            rating = float(arg)
        elif opt == '-o':
            out_file = arg
        elif opt == '-h':
            print(HELP_TEXT)
        else:
            print("Unknown option:", opt)
            print(HELP_TEXT)
            sys.exit()

    if file:
        users_file = file[0]

    main(users_file=users_file, out_file=out_file, countries=country,
         genders=gender, gen_prob=gen_prob, handles=handle, ranks=rank,
         rating=rating, orgs=org)


def main(users_file=None, out_file=None, countries=[], genders=[], gen_prob=0.5, handles=[],
         ranks=[], orgs=[], rating=1000):

    if users_file is None:
        users_file = input("Users file to filter: ")
    users_list = collection.common.get_json_data(users_file)

    if out_file is None:
        out_file = 'filtered.data'

    try:
        users = []
        i = 0
        for user in users_list:
            if (_has_field('country', user, countries)
                    and _has_field('gender', user, genders)
                    and _field_greater('gender_probability', user, gen_prob)
                    and _has_field('handle', user, handles)
                    and _has_field('organization', user, orgs)
                    and _has_field('rank', user, ranks)
                    and _field_greater('rating', user, rating)):
                i += 1
                print("#", i, " -- User:", user['handle'])
                users.append(user)

    finally:
        collection.common.write_json_data(out_file, users)


def _split_and_lower(args):
    t = [x.lower() for x in args.strip().split()]
    for i, arg in enumerate(t):
        arg = ' '.join(arg.split('-'))
        t[i] = arg
    return t


def _has_field(field, user, valid):
    if not valid or valid is None:
        return True

    if field in user and user[field].lower() in valid:
        return True
    return False


def _field_greater(field, user, value):
    if field in user and float(user[field]) >= value:
        return True
    return False


HELP_TEXT = 'some help text'


if __name__ == "__main__":
    _entry()
