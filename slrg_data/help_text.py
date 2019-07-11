# Github ###############################################################

_git_options = """
Options
~~~~~~~
 Unless otherwise stated all options default to config file 
If the value in the config file is None the user will be asked to
input values.

-h
    Print out help text.

-l <programming language>
    The programming language that source is being collected from.
    Determines the table to use and the file extensions. See config.py
    for more info.
    * Default is to ask for it.

-i <input data file>
    The file containing a list of codeforces user records.
    * Default is to ask for it.

-s <start index>
    The record to start processing first.

-c <records to process>
    The number of records to process in total.

-u <database username>
    The database username.

-p <database password>
    The database password.

--git=<github username>
    The username of the github account to use with API calls.

--gitpass=<github password>
    The password for the github account.
"""


COLLECT_GIT_PROJECTS = """
$ slrg-git-projects [-h] [-l < programming language > ]
    [-i < input data file > ] [-s < start index > ] [-c < records to process > ]
    [-u < database username >] [-p < database password > ]
    [--git = <github username >] [--gitpass = <github password > ]
""" + _git_options


COLLECT_GIT_COMMITS = """
$ slrg-git-commits [-h] [-l <programming language>]
    [-i <input data file>] [-s <start index>]
    [-c <records to process>] [-u <database username>]
    [-p <database password>] [--git=<github username>]
    [--gitpass=<github password>]
""" + _git_options


# Codeforces ###########################################################

COLLECT_CODEFORCES = """
$ slrg-codeforces [-h] [-l <programming language>]
    [-i <input data file>] [-s <start index>]
    [-c <number of records to process>] [-u <database username>]
    [-p <database password>]

Options
~~~~~~~
Unless otherwise stated all options default to config file and if
the value in the config file is None the user will be asked to
input values.

-h
    Print out help text.

-i <input data file>
    The file containing a list of codeforces user records.
    * Default is to ask for it.

-s <start index>
    The record to start processing first.

-c <records to process>
    The number of records to process in total.

-u <database username>
    The database username.

-p <database password>
    The database password.
"""


GENDER_CODEFORCES = """
$ slrg-gender-codeforces [-h] [-i <codeforces users file>]
    [-o <output file>] [-m <missing gender file>]
    [-t <gender table name>] [-u <databse username>]
    [-p <database password>]

Options
~~~~~~~

-h
    Print help text.

-i <codeforces user file>
    The file containing a list of codeforces user records. If left blank
    it will be prompted for.

-o <output file>
    The file to write the gendered results to.
    * Default is gendered.data

-m <missing gender file>
    The file to write records that cannot be gendered yet because
    the gender API is unavailable.
    * Default is missing_gender.data

-t <gender table name>
    The name of the gender table in the database.
    * Defaults to value in config file. If the value in config is None
      it will be asked for.

-u <database username>
    The database username.
    * Defaults to value in config file. If the value in config is None
      it will be asked for.

-p <database password>
    The database password.
    * Defaults to value in config file. If the value in config is None
      it will be asked for.
"""


FILTER_CODEFORCES = """
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

-h
    Print help text.

-o <output file>
    The file to write the results to.

-i <codeforces user file>
    The file containing a list of codeforces user records.
    * If left blank it will be asked for.

--country=<country(s)>
    One or more countries to look for.

--gender=<gender(s)>
    The gender(s) to look for.

--gen_prob=<gender probability>
    The minimum gender probability to accept. Range [0.0, 1.0]
    * Defaults to 0.5

--handle=<handle(s)>
    The handles to look for.

--org=<organization(s)>
    The organizations to look for.

--rank=<rank(s)>
    The codeforces ranks to look for.

--rating=<rating>
    The minimum codeforces rating to accept.
    * Default is 1000.
"""


# Other ################################################################

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
    * Defaults to value in config file, if the value in config is None
      it will be asked for.

-p <database password>
    The database password.
    * Defaults to value in config file. If the value in config is None
      it will be asked for.
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
     wildcards and other regex are not supported.
"""
