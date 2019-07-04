import sys
import os
import getopt

if __name__ == '__main__':
    import collection
    from help_text import COLLECT_CODEFORCES as HELP_TEXT
else:
    from . import collection
    from .help_text import COLLECT_CODEFORCES as HELP_TEXT

try:
    sys.path.append(collection.common.SLRG_DIR)
    import config  # nopep8
except ModuleNotFoundError:
    print('Config Error: Could not find config.py.',
          'Please make sure you have run slrg-install.')
    sys.exit()


def _entry():
    _script(sys.argv[1:])


def _script(argv):
    # Declare variables
    lang = None
    file = None
    start = None
    count = None
    db_login = None
    db_passwd = None

    # Parse command line arguments
    try:
        opts, _ = getopt.getopt(argv, "l:i:s:c:u:p:h")
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
        elif opt == '-h':
            print(HELP_TEXT)
            return

    main(lang=lang, file=file, start=start, count=count, db_login=db_login,
         db_passwd=db_passwd)


def main(lang=None, file=None, start=None, count=None, db_login=None,
         db_passwd=None):

    script_name = 'codeforces'

    database = collection.script.make_database(config.database,
                                               login=db_login,
                                               passwd=db_passwd)

    limits = collection.script.make_cf_limits(
        start, count, config.limits[script_name])
    info = collection.script.make_cf_info(
        lang, file, limits, script_name, config.config)

    log_dir = os.path.join(collection.common.SLRG_DIR, 'logs', script_name)
    log = collection.common.Log(log_dir, script_name)
    collection.script.remove_old_logs(log_dir, config.max_logs_to_keep)

    collector = collection.codeforces.CfSeleniumCollector(database, info, log)


if __name__ == '__main__':
    _entry()
