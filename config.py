"""Configuration values required for running the scripts.

For most uses setting the database account information, collection languages, and GitHub account information will be the only things that may require setup.

Unless otherwise indicated any values left as None will be asked for when running scripts. Unless they are not overridden by command line options or function parameters.

See the :ref:`Scripts section <scripts>` for information on overriding the configuration file values with command line options or function parameters.

.. warning:: Any passwords stored in the configuration file or passed to the scripts will be stored as plain text in the program. If you don't want this then leave password fields blank. Then passwords will be collected by pythons *getpass* module and passed directly to the *pymysql* and *requests* modules for operations that require authentication.

Fields
------

database
    * host
        The host address of your database. If the database is on your computer then this will be localhost.
    * name
        The name of the database.
    * login
        The name of your account for the database.
    * passwd
        The password to your database account.

table
    **No values in table can be None**

    Each process has it's own column schema and tables using that schema for each language collected.

    If you collect for a different language with any of the processes you can add the name of the table :code:`'language': 'table_name'`.

    * git_projects
        - c++
            Name of the table to store C++ samples.
        - python
            Name of the table to store Python samples.
        - java
            Name of the table to store Java samples.
        - columns
            A list of column names in tables for storing GitHub project samples.

    * git_commits
        - c++
            Name of the table to store C++ samples.
        - python
            Name of the table to store Python samples.
        - java
            Name of the table to store Java samples.
        - columns
            A list of column names in tables for storing GitHub commits samples.

    * codeforces
        - name
            Name of the table to store all samples.
        - columns
            A list of column names in tables for storing Codeforces submission
            samples.

extensions
    **You must set these for the language you are collecting for. Otherwise no files will be collected.**

    * Maps a programming language to a list of file extensions that will be collected for that language.
    * For example :code:`'c++': ['.cc','.cpp']` would collect all C++ source code files but no headers. If you wanted to collect header files as well you could change it to be :code:`'c++': ['.cc','.cpp','.h','.hpp']`.

exclude
    **The lists cannot be None, But can be empty if you wish to collect everything with a valid extension**

    * files
        - A list of all file names that should be excluded from collection.
    * dirs
        - A list of all directories that should not be searched for files during collection.

cf_languages
    **Cannot be None.**
    
    If collect is left empty no samples will be collected. The exclude keeps a language that has a collected language as a part of its name from being collected. Ie) java/javascript or c/c++. If the longer names are not excluded they will be mistakenly collected.

    * collect
        - A list of programming languages to collect samples for.
    * exclude
        - A list of programming languages to exclude from collection.

git_acct
    * login
        - A GitHub account username.
    * passwd
        - The password for the  github account.

limits
    * All scripts
        - start
            The first record to process when running a script. It is best to leave this as None and give it when running the scripts.
        - count
            The number of records to process before stopping. Useful if you don't want the scrip to run for too long or you only need a certain number of records to be processed.
    * codeforces(only)
        - subs_start
            The first submission to collect when processing a user. Should most likely be left at 1 unless you have modified the script to collect from a submission page other than the first.
        - subs_count
            The maximum number of subs to collect. If selenium is being used this should never be more than 50.
        - max_subs
            The maximum number of samples to store in the database for a user.
        - max_no_source
            The maximum number of samples to try to collect that have no source before moving onto the next user. Don't change unless you are not using selenium.

max_logs
    * The maximum number of logs to keep. **Cannot be None**

save_missing
    * Wether or not to save records when the gender API rate limit has been reached. Records will be saved in a file when the script finishes in slrg/git/missing

.. warning:: The scripts do not check on how many files are stored in the missing directory. If you set it to True and never clean the directory it could become very large over time.

config
    * A dict of the config file's contents. Each of the above attributes is a field in the dict.

"""

# Information for the MySQL database connection
# Values can be None
# login and passwd can be given as command line options
database = {
    'host': 'mysql-8-p.uleth.ca',
    'login': None,
    'name': 'sfa-slrg_data',
    'passwd': None
}

# Table information for each script
# This includes table names for each language (if applicable) and the
# table column schema.
tables = {
    'git_projects': {
        'c++': 'git_projects_cpp',
        'python': 'git_projects_py',
        'java': 'git_projects_java',
        'columns': [
            "user_id", "user_login", "user_fullname",
            "gender", "gender_probability",
            "user_company", "user_created", "user_type",
            "user_country_code", "user_state", "user_city", "user_location",
            "project_id", "project_url", "project_name",
            "project_language", "project_created",
            "file_hash", "file_name", "file_contents", "file_lines"
        ]
    },
    'git_commits': {
        'c++': 'git_commits_cpp',
        'python': 'git_commits_py',
        'java': 'git_commits_java',
        'columns': [
            "user_id", "user_login", "user_company", "user_created",
            "user_type", "user_country_code", "user_state", "user_city",
            "user_location", "project_id", "project_url", "project_name",
            "project_language", "project_created", "commit_id", "commit_sha",
            "commit_created", "file_sha", "file_name", "file_contents",
            "file_changes"
        ]
    },
    'codeforces': {
        'name': 'cf_refine',
        'columns': [
            "submission_id", "source_code", "programming_language",
            "problem_name", "difficulty", "participant_type", "time", "year",
            "month", "day", "handle", "first_name", "last_name", "gender",
            "gender_probability", "country", "city", "organization",
            "contribution", "user_rank", "rating", "max_rank", "max_rating",
            "registered"
        ]
    },
    'gender': 'genders'
}

# Fields that are present in the JSON records for each collection script
# Should not be changed, unless you are sure you know what you are doing.
# These are directly related to API call returns or JSON results
# from BigQuery.
fields = {
    'git_projects': [
        'users_id', 'login', 'user_fullname',
        'gender', 'gender_probability',
        'company', 'type', 'users_created_at',
        'country_code', 'state', 'city', 'location',
        'projects_id', 'url', 'name', 'language',
        'projects_created_at'
    ],
    'git_commits': [
        'users_id', 'login', 'company', 'users_created', 'type',
        'country_code', 'state', 'city', 'location', 'projects_id', 'url',
        'name', 'language', 'projects_created', 'id', 'sha', 'created_at'
    ],
    'codeforces': [
        "handle", "firstName", "lastName", "gender", "gender_probability",
        "country", "city", "organization", "contribution", "rank", "rating",
        "maxRank", "maxRating", "registrationTimeSeconds"
    ]
}

# File extensions of files to include for each language
# You can add new languages or extensions as needed
extensions = {
    'c++': ['.cc', '.cpp'],
    'python': ['.py'],
    'java': ['.java']
}

# Files and directories to be excluded when searching for source
# Only utilized by the git_projects collection right now
exclude = {
    'files': [
        '__init__.py',
        'setup.py',
        'version.py',
        'test.py'
    ],
    'dirs': [
        'lib',
        'libs',
        'library',
        'libraries',
        'ext',
        'etxs',
        'extension',
        'extensions',
        'bin',
        'test',
        'tests',
        'samples',
        '.git'
    ]
}

# Languages to collect and exclude with codeforces collection
# The exclusion is because the languages are matched with string.find so
# In some cases (like with Java and Javascript) it is
# possible to match more than one language.
cf_languages = {
    'collect': ['C++', 'Python', 'Java'],
    'exclude': ['Javascript']
}

# The github account to use when needed
# Values can be None or given as command line options
git_acct = {
    'login': 'slrg-uleth',
    'passwd': None
}

# The starting entry and max entries to process for each script
# Values can be None or given as command line options
limits = {
    'git_projects': {
        'start': None,
        'count': 10000
    },
    'git_commits': {
        'start': None,
        'count': 10000
    },
    'codeforces': {
        'start': None,
        'count': 100,
        'sub_start': 1,  # Starts at 1 not 0
        'sub_count': 50,
        'max_subs': 50,
        'max_no_source': 50,
    }
}

# Maximum logs to keep per file
max_logs_to_keep = 10

# Wether or not to save gender records that may have a gender, but the
# gender API is down or there was an error looking up a name.
save_missing = False

# To make it possible to pass the whole config file contents around
# easily if needed
config = {
    'database': database,
    'tables': tables,
    'fields': fields,
    'extensions': extensions,
    'exclude': exclude,
    'git_acct': git_acct,
    'limits': limits,
    'cf_languages': cf_languages,
    'save_missing': save_missing,
}
