COLLECT_GIT_PROJECTS = """
$ python3 collect_git_projects.py [-h] [-l < programming language > ]
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


SELECT = """
$ python3 select.py [-h] [-o <output file>] [-i <input sql file>]
    [-u <database username>] [-p <database password>]

Options
~~~~~~~

-h
    Print help text.

-j | -c
    Output in JSON or CSV format.
    * If both are given the first will be used.

-o <output file>
    The file to write the results to.
    * Must be relative to the slrg_data_collection directory.

-i <input sql file>
    A file with the SQL SELECT query. 
    * Must be relative to the slrg_data_collection directory.

-u <database username>
    The database username.
    * Defaults to value in config file. If config value is None
      it will be asked for.

-p <database password>
    The database password.
    * Defaults to value in config file. If config value is None
      it will be asked for.
"""


COLLECT_CODEFORCES = """
Some help text
"""
