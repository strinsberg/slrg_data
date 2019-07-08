import os
import sys
import getopt
import json

if __name__ == '__main__':
    import collection
    from help_text import COLLECT_GIT_PROJECTS as HELP_TEXT
else:
    from . import collection
    from .help_text import COLLECT_GIT_PROJECTS as HELP_TEXT

try:
    sys.path.append(collection.common.SLRG_DIR)
    import test_config as config  # nopep8, pylint: disable=import-error
except ModuleNotFoundError:
    print('Config Error: Could not find config.py.',
          'Please make sure you have run slrg-install.')
    sys.exit()


def _entry():
    _script(sys.argv[1:])


def _script(argv):
    """Collect source code from GitHub commits.

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
        collector = collection.github.CommitsCollector(database, info, log)
        return collector.main()

    except collection.script.ScriptInputError as err:
        print('\n***', err)


if __name__ == "__main__":
    _entry()
