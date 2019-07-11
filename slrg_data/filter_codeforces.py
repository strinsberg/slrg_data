"""Filter out records for codforces users that satisfy any given
conditions and write them to a new file.

If no conditions are given then all the users will be taken.

Usage
=====
As a command line script.

Run::

    $ slrg-filter-codeforces [-h] [-o <output file>]
        [-i <codeforces users file>] [--country=<country(s)>]
        [--gender=<gender(s)>] [--gen_prob=<min gender probability>]
        [--handle=<handles(s)>] [--org=<organization(s)>] [rank=<rank(s)]
        [--rating=<min rating>]

Options
~~~~~~~
If multiple values are given separate them by a space and surround
the list with quotes. Ie) 'canada russia'
Values that are made of multiple word should have a ~ inserted
between the words. Ie) 'united~states' or 'legendary~grandmaster'
All category options default to accepting all values unless otherwise
specified.

**-h**
    Print help text.

**-o <output file>**
    The file to write the results to.

**-i <codeforces user file>**
    The file containing a list of codeforces user records. If left blank
    it will be prompted for.

**--country=<country(s)>**
    One or more countries to look for.

**--gender=<gender(s)>**
    The gender(s) to look for.

**--gen_prob=<gender probability>**
    The minimum gender probability to accept. Range [0.0, 1.0]
    Defaults to 0.5

**--handle=<handle(s)>**
    The handles to look for.

**--org=<organization(s)>**
    The organizations to look for.

**--rank=<rank(s)>**
    The codeforces ranks to look for.

**--rating=<rating>**
    The minimum codeforces rating to accept.
    Default is 1000.
"""
# Standard python modules
import sys
import getopt

# Local imports
if __name__ == '__main__':
    import collection
    from help_text import FILTER_CODEFORCES as HELP_TEXT
else:
    from . import collection
    from .help_text import FILTER_CODEFORCES as HELP_TEXT

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
    """Entry point for the Script."""
    _script(sys.argv[1:])


def _script(argv):
    """Processes command line arguments and calls main with their values.

    See module details for more info on command line options.

    Args:
        argv (list of str): The list of command line options and args
            not containing the script name.
    """
    # Declare some variables
    out_file = None
    users_file = None
    country = []
    gender = []
    gen_prob = 0.5
    handle = []
    org = []
    rank = []
    rating = 1000

    # Parse command line arguments
    try:
        opts, _ = getopt.getopt(argv, "i:o:h",
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
        elif opt == '-i':
            users_file = arg
        elif opt == '-o':
            out_file = arg
        elif opt == '-h':
            print(HELP_TEXT)
        else:
            print("Unknown option:", opt)
            print(HELP_TEXT)
            sys.exit()

    main(users_file=users_file, out_file=out_file, countries=country,
         genders=gender, gen_prob=gen_prob, handles=handle, ranks=rank,
         rating=rating, orgs=org)


def main(users_file=None, out_file=None, countries=[], genders=[],
         gen_prob=0.5, handles=[], ranks=[], orgs=[], rating=1000):
    """Filters out a list of users that satisfy the given conditions and
    writes the results to a new file.

    If values are not given then then that category will not be filtered.

    Args:
        users_file (str): The name of the Codeforces user file. If it is
            None then the user will be prompted for it.
        out_file (str): The name of the file to write the results to. If
            None defaults to 'filtered.data'
        countries (list of str): A list of countries to accept.
        genders (list of str): A list of genders to accept.
        gen_prob (float): The lowest gender probability to accept. The
            Default is 0.5.
        handles (list of str): A list of handles to accept.
        ranks (list of str): A list of ranks to accept.
        orgs (list of str): A list of organizations to accept.
        rating (int): The lowest rating to accept.
    """
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


# Helpers ##############################################################

def _split_and_lower(args):
    """Splits up a list of arguments and lowers them all.

    In addition to splitting on spaces. Any multiword arguments must be
    connected by a ~ so they can be seen as one argument, but then split
    on the ~ to become the proper string.

    Ie) if 'canada united states' are passed as args they will be split
    as ['canada' ,'united', 'states'], but if they are passed as
    'canada united~states' then they will be properly split as
    ['canada', 'united states']

    Args:
        args (str): A string of arguments to a command line option.

    Returns:
        list of str: A list of the arguments. All multiword arguments
            will have the ~ replaced with a space.
    """
    t = [x.lower() for x in args.strip().split()]
    for i, arg in enumerate(t):
        arg = ' '.join(arg.split('~'))
        t[i] = arg
    return t


def _has_field(field, user, valid):
    """Checks to see if the value of a field in a user record is valid.

    Args:
        field (str): The field to check.
        user (str): The user record.
        valid (list of str): A list of all the acceptable values for
            user[field].

    Returns:
        bool: True if the fields value is in valid, otherwise false.
    """
    if not valid or valid is None:
        return True

    if field in user and user[field].lower() in valid:
        return True
    return False


def _field_greater(field, user, value):
    """Checks to see if the value of a field in a user record is >= the
    given value.

    Args:
        field (str): The field to check.
        user (str): The user record.
        value (float): The lowest acceptable value.

    Returns:
        bool: True if the fields value >= value, otherwise false.
    """
    if field in user and float(user[field]) >= value:
        return True
    return False


# Run ##################################################################

if __name__ == "__main__":
    _entry()
