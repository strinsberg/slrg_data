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


def make_git_info(lang, filename, login, passwd, script_name, config):
    """Makes a github.CollectionInfo object for the script to use.

    Args:
        lang (str): The programming language to collect source in.
        filename (str): The file the project data is stored in.
        login (str): A Github username. Can be None.
        passwd (str): The Github password. Can be None.
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

    limits = common.LimitData(config.limits['start'],
                              config.limits['count'])

    login = config.git_acct['login'] if login is None else login
    passwd = config.git_acct['passwd'] if passwd is None else passwd
    git_data = github.GithubData(login, passwd)

    return github.GitCollectionInfo(records, table, validation, limits,
                                    git_data)


def get_file_path(filename, script_name):
    file = null_arg_str(filename, "Data file: ")
    if os.path.isfile(file):
        return file
    return os.path.join('data', script_name, file)


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
