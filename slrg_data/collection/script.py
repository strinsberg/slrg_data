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
        db_config (dict): A dictionary with database information. See
            slrg_data_collection.config.py
        host (str): The database hostname.
        login (str): The database username.
        passwd (str): The database password.
        name (str): The database name.

    Returns:
        common.Database: A Database object with the given information.
    """
    host = null_arg_str(host, db_config['host'], "Database host: ")
    name = null_arg_str(name, db_config['name'], "Database name: ")
    login = null_arg_str(login, db_config['login'])
    passwd = null_arg_str(passwd, db_config['passwd'])

    return common.Database(host, login, name, passwd)


def make_limits(start, count, default):
    start = null_arg_int(start, default['start'], "Starting index: ")
    count = null_arg_int(count, default['count'], "Entries to process: ")

    return common.LimitData(start, count)


def make_git_data(login, passwd, default):
    login = default['login'] if login is None else login
    passwd = default['passwd'] if passwd is None else passwd

    return github.GithubData(login, passwd)


def make_git_info(lang, filename, git_data, limits, script_name, config):
    """Makes a github.CollectionInfo object for the script to use.

    Args:
        lang (str): The programming language to collect source in.
        filename (str): The file the project data is stored in.
        git_data (github.GitData): Github account data.
        limits (common.LimitData): Limits for the collection.
        script_name (str): The name of the script calling it.
        config (dict): The contents of the config file in a dict. See
            :ref:`Configuration <config_lab>` for more details.

    Returns:
        collection.github.CollectionInfo: A CollectionInfo object with
        the necessary information for source collection.
    """
    if lang is None:
        lang = input('Language: ').lower()

    file_path = get_file_path(filename, script_name)
    records = common.RecordsData(file_path, config['fields'][script_name])

    table = common.TableData(config['tables'][script_name][lang],
                             config['tables'][script_name]['columns'])

    validation = common.ValidationData(config['extensions'][lang],
                                       config['exclude']['files'],
                                       config['exclude']['dirs'])

    return github.GitCollectionInfo(records, table, validation, limits,
                                    git_data)


def get_file_path(filename, script_name):
    # This is where the necessary data to get the data file while running
    # the script anywhere is going to need to be.
    file = null_arg_str(filename, None, "Data file: ")
    if os.path.isfile(file):
        return file
    # Wrap this in an if clause and return an error message if there
    # is no file found
    return os.path.join('data', script_name, file)


def null_arg_str(arg, default, prompt=None):
    """If a given arg is None then ask for a value.

    Args:
        arg (str): A value or None.
        prompt (str): The prompt to display if input is required.
            Default is None.

    Returns:
        str: The arg, default, or input with prompt. If arg, default,
            and prompt are None then None.
    """
    if arg is not None:
        return arg

    if default is not None:
        return default

    return input(prompt) if prompt is not None else prompt


def null_arg_int(arg, default, prompt):
    """If a given arg is None then ask for a value.

    Args:
        arg (str): A value or None.
        prompt (str): The prompt to display if input is required.

    Returns:
        int: The arg or an int of the collected user input if arg is None.
    """
    return int(null_arg_str(arg, default, prompt))
