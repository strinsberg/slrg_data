COLLECT_GIT_PROJECTS = """
$ slrg-git-projects [-h] [-l < programming language > ]
    [-i < input data file > ] [-s < start index > ] [-c < records to process > ]
    [-u < database username >] [-p < database password > ]
    [--git = <github username >] [--gitpass = <github password > ]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the config file is None the user will be asked to input values.

-h
    Print out help text.

-l < programming language >
    The programming language that source is being collected from.
    Determines the table to use and the file extensions. See config.py
    for more info.
    * Default is to ask for it.

-i < input data file >
    The data file to process. Can be a filepath relative to the current
    directory or a file name in the data/git_projects directory.
    * Default is to ask for it.

-s < start index >
    The entry to start processing first.

-c < records to process >
    The count for number records to process in total.

-u < database username >
    Database username.

-p < database password >
    The database password.

--git = <github username >
    The username of the github account to use with API calls.

--gitpass = <github password >
    The password for the github account.
"""

COLLECT_GIT_COMMITS = """
    $ slrg-git-commits [-h] [-l <programming language>]
        [-i <input data file>] [-s <start index>]
        [-c <records to process>] [-u <database username>]
        [-p <database password>] [--git=<github username>]
        [--gitpass=<github password>]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the config file is None the user will be asked to input values.

-h
    Print out help text.

-l <programming language>
    The programming language that source is being collected from.
    Determines the table to use and the file extensions. See config.py
    for more info.
    * Default is to ask for it.

-i <input data file>
    The data file to process. Can be a filepath relative to the current
    directory or a file name in the data/git_projects directory. 
    * Default is to ask for it.

-s <start index>
    The entry to start processing first.

-c <records to process>
    The count for number of records to process in total.

-u <database username>
    Database username.

-p <database password>
    The database password.

--git=<github username>
    The username of the github account to use with API calls.

--gitpass=<github password>
    The password for the github account.
"""

SELECT = """
$ slrg-select [-h] [-j | -c] [-n] [-o <output file>]
    [-i <input sql file>] [-u <database username>]
    [-p <database password>]

Options
~~~~~~~

-h
    Print help text.

-j | -c
    Output in JSON or CSV format.
    *If both are given the first will be used.

-n
    if Selected a header row will be printed at the top of the csv with
    column names used in select statement. 
    * Only applicable to CSV output.

-o <output file>
    The file to write the results to.

-i <input sql file>
    A file with the SQL SELECT query.
    * Default is to ask for a SELECT statement.

-u <database username>
    The database username.
    * Defaults to value in config file, if config value is None
      it will be asked for.

-p <database password>
    The database password.
    * Defaults to value in config file. If config value is None
      it will be asked for.
"""


COLLECT_CODEFORCES = """
slrg-codeforces [options]
"""

GENDER_CODEFORCES = """
slrg-gender-codeforces [options]
"""

FILTER_CODEFORCES = """
$ slrg-filter-codeforces [-h] [-o <output file>]
    [-i <codeforces users file>] [--country=<country(s)>]
    [--gender=<gender(s)>] [--gen_prob=<min gender probability>]
    [--handle=<handles(s)>] [--org=<organization(s)>] [rank=<rank(s)]
    [--rating=<min rating>]
"""

COMBINE_JSON = """
slrg-combine-json [-h] [-o <output file>] [-f < raw json folder> ]
        [-g < group size > ] [<json files>]

Options
~~~~~~~

-h
    print help text.

-o <output file>
    The name without an extension to use for the output files.
    If more than one file is created a number will be added to all
    files after the first. eg) file.data, file1.data, etc.
    * Default is to ask for a name.

-f <raw json folder>
    The name of a folder to store the uncombined json files in.
    * Default is to DELETE all uncombined json files.

-g <group size>
    The number of json files to combine for each data file created.
    * Default is to combine them into one file (up to 10,000).

<json files>
    The names of all the json files to combine.
    * Default is to collect all json files in current folder.
    ** wildcards and other regex are not supported.
"""
