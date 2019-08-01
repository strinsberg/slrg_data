"""Script to combine multiple JSON files gathered from an API.

Suitable for any api that returns results as JSON records that are
not already in a list (like BigQuery).

The combined .data files contain the JSON records in a list. These new
files can be opened by the python json library as a list of dict.

Usage
-----
Run as a command line script in the folder that contains the JSON files
you want combined.

::

    $ slrg-combine-json [-h] [-o <output file>] [-f < raw json folder> ]
        [-g < group size > ] [<json files>]

Options
~~~~~~~

**-h**
    print help text.

**-o <output file>**
    The name without an extension to use for the output files.
    If more than one file is created a number will be added to all files
    after the first. eg) file.data, file1.data, file2.data, etc.
    Default is to ask for a name.

**-f <raw json folder>**
    The name of a folder to store the uncombined json files in.
    Default is to delete all uncombined json files.

**-g <group size>**
    The number of json files to combine for each data file created.
    Default is to combine them into one file (up to 10,000).

**<json files>**
    The names of all the json files to combine.
    Default is to collect all json files in current folder as
    wildcards are not supported.

"""
# Standar python modules
import os
import json
import shutil
import sys
import getopt

# Local imports
from . import collection
from .help_text import COMBINE_JSON as HELP_TEXT


# Script and Main Functions ############################################

def _entry():
    """Entry point for the script."""
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
    raw_folder = None
    group_size = None
    delete = False

    # Parse command line arguments
    try:
        opts, filenames = getopt.getopt(argv, "o:f:g:hd")
    except getopt.GetoptError:
        print(HELP_TEXT)
        sys.exit()

    for opt, arg in opts:
        if opt == '-o':
            out_file = arg
        elif opt == '-f':
            raw_folder = arg
        elif opt == '-g':
            group_size = int(arg)
        elif opt == '-d':
            delete = True
        elif opt == '-h':
            print(HELP_TEXT)
            return

    if not filenames:
        filenames = None

    if raw_folder is None and not delete:
        raw_folder = 'json_folder'

    main(files=filenames, out_file=out_file,
         raw_folder=raw_folder, group_size=group_size)


def main(files=None, out_file=None, raw_folder=None, group_size=None):
    """Main for script to combine json files into .data files.

    See module documentation for more details.

    Args:
        files (list of str): Names of the json files to combine. If None
            all .json files in the current folder will be used.
        out_file (str): The filename to use for the output file(s). If
            more than one file is created numbers will be appended. Will
            also have .data appended to all files created. If None will
            default to 'combined'.
        raw_folder (str): A name of a folder to store the uncombined
            json files after they are combined. If None they will be
            deleted.
        group_size (int): The number of files to use for each combined
            file. If None it defaults to 10000 which in most cases
            should result in all .json files being combined into one
            output file.
    """
    if out_file is None:
        out_file = input('Name for output file(s): ')

    if files is None:
        files = _get_all_json_files()

    if group_size is None:
        group_size = 10000

    combined = _combine_json(files, group_size)
    _write_results(out_file, combined)
    _move_files(files, raw_folder)


# Helpers ##############################################################

def _get_all_json_files():
    """Collects the names of all JSON files in the current directory.

    Returns:
        list of str: A list of the names of all .json files in the
            current directory.
    """
    json_filenames = []
    for file in os.listdir():
        if file.endswith(".json"):
            json_filenames.append(file)
    return json_filenames


def _combine_json(json_filenames, group_size):
    """Combine the records of a JSON file into a list.

    Intended to be used on JSON files in which each line is a new JSON
    record. Will not work on JSON files where records are already in a
    list or are contained inside of another dict.

    The returned list will contain multiple lists of records if group_size
    is small enough that more than one group is created.

    Args:
        json_filenames (list of str): A list of JSON filenames to combine.
        group_size (int): The number of files to combine for each group.

    Returns:
        A list containing lists of JSON dicts.
    """
    combined = []
    contents = []

    for i, file in enumerate(json_filenames):
        print("Combining", file)

        # Add file contents to results
        with open(file) as f:
            records = f.read().splitlines()
        for record in records:
            contents.append(json.loads(record))

        # If group is done store the combined results
        if (i + 1) % group_size == 0 or i == len(json_filenames) - 1:
            combined.append(contents)
            contents = []

    return combined


def _write_results(out_file, combined):
    """Write the lists of combined json records to .data files.

    If more than one file is created numbers will be appended to the
    out_file name.

    Args:
        out_file (str): The filename to write the results to.
        combined (list of lists of JSON dicts): A list containing one
            or more lists of JSON records.
    """
    ext = "data"
    for i, contents in enumerate(combined):
        if i == 0:
            name = "{}.{}".format(out_file, ext)
        else:
            name = "{}{}.{}".format(out_file, i + 1, ext)

        with open(name, 'w') as f:
            json.dump(contents, f)
        print("** Created", name)


def _move_files(filenames, folder):
    """Move filenames to the raw_folder or delete them.

    **If raw_folder is None the files will be deleted.**

    Args:
        filenames (list of str): A list of file names that are to be
            moved or deleted.
        folder (str): The name of the folder to move the files to.
            If None the files will be deleted.
    """
    if folder is not None:
        if not os.path.isdir(folder):
            os.mkdir(folder)

        for file in filenames:
            print("Moving", file)
            os.rename(file, os.path.join(folder, file))

    else:
        for file in filenames:
            print("Deleting", file)
            os.remove(file)
