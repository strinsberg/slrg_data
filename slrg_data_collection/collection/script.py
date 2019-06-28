"""Helper functions for running scripts."""
import json
import os
from . import common
from . import github
from . import codeforces


def make_database(db_config, host=None, login=None, passwd=None, name=None):
    """Creates a common.Database object with given information.

    All arguments (except db_config) default to None. If they are None
    then db_config will be checked for a value. If that is None then
    the user will be prompted to input a value.

    Args:
        db_config (dict): A dictionary with databse information. See
            slrg_data_collection.config.py
        host (str): The database hostname.
        login (str): The database username.
        passwd (str): The database password.
        name (str): The database name.

    Returns:
        common.Database: A Database object with the given information.
    """
    if host is None:
        host = null_arg_str(db_config['host'], "Database host: ")
    if name is None:
        name = null_arg_str(db_config['name'], "Database name: ")

    return common.Database(host, login, name, passwd)


def make_limits(script, limits, start=None, count=None):
    """Constructs a dictionary with a start and count field.

    Args:
        script (str): The name of the script being run.
        limits (dict): A set of default limits.
        start (int): The starting index.
        count (int): The number of entries to process.

    Returns:
        dict: A dict with start and count values.
    """
    if start is None:
        start = null_arg_int(limits[script]['start'], "Start index: ")
    if count is None:
        count = null_arg_int(limits[script]['count'], "Entries to process: ")

    return {'start': start, 'count': count}


# Takes way to many params. Split up or fix somehow.
def make_git_info(lang, file, login, passwd, script_name, config):
    """Makes a github.CollectionInfo object for the script to use.

    Args:
        lang (str): The projramming language to collect source in.
        file (str): The file the project data is stored in.
        login (str): A Github username. Can be None.
        passwd (str): The Github password. Can be None.
        script_name (str): The name of the script calling it.

    Returns:
        collection.github.CollectionInfo: A CollectionInfo object with
        the necessary information for source collection.
    """
    if lang is None:
        lang = input('Language: ').lower()

    file = input('Data file: ') if file is None else file
    if os.path.isfile(file):
        file_path = file
    else:
        file_path = os.path.join('data', script_name, file)

    git = {}
    git['login'] = config['git_acct']['login'] if login is None else login
    git['passwd'] = config['git_acct']['passwd'] if passwd is None else passwd

    table = config['tables'][script_name][lang]
    columns = config['tables'][script_name]['columns']
    extensions = config['extensions'][lang]

    return github.CollectionInfo(
        file_path, columns, table, extensions, config['exclude'], git)


def null_arg_str(arg, prompt):
    """If a given arg is None then ask for a value.

    Args:
        arg (str): A value or None.
        prompt (str): The prompt to display if input is required.

    Returns:
        str: The arg or the collected user input if arg is None.
    """
    if arg is None:
        return input(prompt)
    return arg


def null_arg_int(arg, prompt):
    """If a given arg is None then ask for a value.

    Args:
        arg (str): A value or None.
        prompt (str): The prompt to display if input is required.

    Returns:
        int: The arg or an int of the collected user input if arg is None.
    """
    return int(null_arg_str(arg, prompt))
