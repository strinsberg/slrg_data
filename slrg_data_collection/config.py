"""Configuration values required for running the scripts.

Where indicated values can be set to None and scripts will prompt for
input when run.

Attributes:
    database: ??
    table: ??
    extensions: ??
    exclude: ??
    git_acct: ??
    limits: ??
"""

# Information for the MySQL database connection
# Values can be None
# login and passwd can be given as command line options
database = {
    'host': 'localhost',
    'login': 'root',
    'name': 'slrg_data',
    'passwd': None
}

# Table information for each script
# This includes table names for each language (if applicable) and the
# table column schemas?
tables = {
    'git_projects': {
        'c++': 'git_projects_cpp',
        'python': 'git_projects_py',
        'java': 'git_projects_java',
        'columns': []
    },
    'git_commits': {
        'c++': 'git_commits_cpp',
        'python': 'git_commits_py',
        'java': 'git_commits_java',
        'columns': []
    },
    'codeforces': {
        'columns': []
    }
}

# Fields that are present in the JSON records for each collection script
# Should not be changed, unless you are sure you know what you are doing.
fields = {
    'git_projects': [
        'users_id',
        'login',
        'user_fullname',
        'gender',
        'gender_probability',
        'company',
        'users_created_at',
        'type',
        'country_code',
        'state',
        'city',
        'location',
        'projects_id',
        'url',
        'name',
        'language',
        'projects_created_at'
    ],
    'git_commits': [],
    'codeforces': []
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
        'version.py'
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
        'start': 0,
        'count': 10000
    },
    'git_commits': {
        'start': 0,
        'count': 10000
    },
    'codeforces': {
        'start': 0,
        'count': 100
    }
}

# To make it possible to pass the whole config file contents around
# easily if needed
config = {
    'database': database,
    'tables': tables,
    'fields': fields,
    'extensions': extensions,
    'exclude': exclude,
    'git_acct': git_acct,
    'limits': limits
}
