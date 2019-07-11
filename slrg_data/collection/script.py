"""Helper functions for running scripts."""
# Standard python modules
import json
import os

# Local imports
from . import common
from . import github
from . import codeforces


# Make Database ########################################################

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


# Make Collection Info #################################################

def make_git_info(lang, filename, git_data, limits, script_name, config):
    """Creates a collection.github.GitCollectionInfo object for use with
    github collection.

    Args:
        lang (str): The programming language to collect source in.
        filename (str): The file the project data is stored in.
        git_data (github.GitData): Github account data.
        limits (common.LimitData): Limits for the collection.
        script_name (str): The name of the script calling it.
        config (dict): The contents of the config file in a dict. See
            :ref:`Configuration <config_lab>` for more details.

    Returns:
        collection.github.GitCollectionInfo: A CollectionInfo object with
        the necessary information for github source collection.
    """
    if lang is None:
        lang = input('Language: ')
    lang = lang.lower()

    file_path = get_file_path(filename)
    records = common.RecordsData(file_path, config['fields'][script_name])

    table = common.TableData(config['tables'][script_name][lang],
                             config['tables'][script_name]['columns'])

    validation = common.ValidationData(config['extensions'][lang],
                                       config['exclude']['files'],
                                       config['exclude']['dirs'])

    return github.GitCollectionInfo(records, table, validation, limits,
                                    git_data)


def make_cf_info(filename, limits, script_name, config):
    """Creates a common.CollectionInfo object for use with codforces
    collection.

    Args:
        filename (str): The file the codeforces user data is stored in.
        limits (codeforces.CfLimitData): Limits for the collection.
        script_name (str): The name of the script calling the function.
        config (dict): The contents of the config file in a dict. See
            :ref:`Configuration <config_lab>` for more details.

    Returns:
        collection.common.CollectionInfo: A CollectionInfo object with
        the necessary information for codeforces source collection.
    """
    file_path = get_file_path(filename)
    records = common.RecordsData(file_path, config['fields'][script_name])

    table = common.TableData(config['tables'][script_name]['name'],
                             config['tables'][script_name]['columns'])

    validation = common.LanguageData(
        config['cf_languages']['collect'], config['cf_languages']['exclude'])

    return common.CollectionInfo(records, table, validation, limits)


# Make Info Components #################################################

def make_limits(start, count, default):
    """Creates a common.LimitData object.

    If the start or count are None then the values in the default
    dict will be used. default must contain keys for
    'start' and 'count'.

    Args:
        start (int): The index of a starting record.
        count (int): The maximum number of records to process.
        default (dict): A dict containing default values for start
            and count.

    Returns:
        common.LimitData: A data object containing limits needed for
        some collection processes.
    """
    start = null_arg_int(start, default['start'], "Starting index: ")
    count = null_arg_int(count, default['count'], "Entries to process: ")

    return common.LimitData(start, count)


def make_cf_limits(start, count, default):
    """Creates a codeforces.CfLimitData object.

    If the start or count are None then the values in the default
    dict will be used. Default must contain keys for 'start', 'count',
    'sub_start', 'sub_count', 'max_subs', 'max_no_source'.

    See codeforces.CfLimitData and config for more details.

    Args:
        start (int): The index of a starting record.
        count (int): The maximum number of records to process.
        default (dict): A dict containing values for all the above
            required keys.

    Returns
        codeforces.CfLimitData: A data object containing all the
        required limit values for the codeforces collection.
    """
    start = null_arg_int(start, default['start'], "Starting index: ")
    count = null_arg_int(count, default['count'], "Entries to process: ")

    return codeforces.CfLimitData(start, count,
                                  default['sub_start'], default['sub_count'],
                                  default['max_subs'], default['max_no_source'])


def make_git_data(login, passwd, default):
    """Creates github.GithubData object using given information.

    If the login or password are None then the values in the default
    dict will be used. There must be keys for 'login' and 'passwd' in
    default.

    Args:
        login (str): A GitHub account username.
        passwd (str): The passwd for the GitHub account.
        default (dict): A dictionary containing default values for
            'login' and 'passwd'

    Returns:
        github.GithubData: A data object containing the username and
        passwd values.
    """
    login = default['login'] if login is None else login
    passwd = default['passwd'] if passwd is None else passwd

    return github.GithubData(login, passwd)


# Helpers ##############################################################

def get_file_path(filename=None):
    """Gets a file path from the filename or asks for it.

    Raises an error if the file does not exist.

    Args:
        filename (str): The path to a file to open. If None then the
            user will be asked for one.

    Returns:
        str: filename or the input filepath.

    Raises:
        ScriptInputError
    """
    file = null_arg_str(filename, None, "Data file: ")
    if os.path.isfile(file):
        return file
    raise ScriptInputError("Input Error: No such file: " + file)


def remove_old_logs(log_dir, max_to_keep):
    """Removes old logs until the number of logs is equal to the
    given max.

    If the number of logs in the directory is <= given max nothing
    will be done.

    Args:
        log_dir (str): Full path to the log dir.
        max_to_keep (int): The number of logs to keep.
    """
    contents = os.listdir(log_dir)

    if len(contents) >= max_to_keep:
        contents = sorted(contents, reverse=True)
        for i, file in enumerate(contents):
            if os.path.isfile and i >= max_to_keep:
                os.remove(os.path.join(log_dir, file))


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
    """Same as null_arg_str but returns the value as an int."""
    return int(null_arg_str(arg, default, prompt))


# Exceptions ###########################################################

class ScriptInputError(Exception):
    """Exception for all errors relating to incorrect script input."""
