.. _scripts:

Scripts
===============

There are two different ways to run the scripts. There results are equivilent. Both methods will look for input files, and write any output files, relative to the directory they are run in.

1. Running at the command line.

    * The details and command line options are listed along with each scripts

2. Running from the interpreter.

    * Instead of command line options pass parameters to the keyword arguments of the scripts main function.
    * Collection scripts will return the number of the next entry to process. If the script is stopped you can pass the return value to the start keyword of the next call to main.

All the scripts that need it have command line options and keyword parameters. Most of them refer to fields that can be set in the config file. If a value is not provided for an option that is required to run the script it will check the config file. If the value in the config file is None then the script will prompt you to enter a value. See the individual script below or the :ref:`Config section <config_lab>` for more information.

There are two issues that can prevent the scripts form running for long periods unattended.

    1. The services can occaisionally disconnect. The database, the websites, or the APIs. These disconnections are difficult to recover from as we don't want to abuse the service by continuing to request things when they are unavailable. Some steps are taken to wait and try again, but after a few tries the script will crash. Usually, it will work properly again when it is restarted.

    2. Since we are cloning a project before processing it, there can be issues downloading large GitHub projects. There should not be too many attempts to download large projects as we are not cloning projects with more than one contributor. This can delay the process or result in a great deal of data useage.


.. _github-projects:

Git Projects Collection
-----------------------

.. automodule:: slrg_data.collect_git_projects
   :members:
   :undoc-members:
   :show-inheritance:


.. _github-commits:

Git Commits Collection
-----------------------

.. automodule:: slrg_data.collect_git_commits
   :members:
   :undoc-members:
   :show-inheritance:


.. _codeforces-collection:

Codeforces Collection
-----------------------

.. automodule:: slrg_data.collect_codeforces
   :members:
   :undoc-members:
   :show-inheritance:


Get Codeforces User List
------------------------

.. automodule:: slrg_data.get_codeforces_user_list
   :members:
   :undoc-members:
   :show-inheritance:


.. _gender-cf:

Gender Codeforces User List
---------------------------

.. automodule:: slrg_data.gender_codeforces
   :members:
   :undoc-members:
   :show-inheritance:


.. _filter-cf:

Filter Codeforces User List
---------------------------

.. automodule:: slrg_data.filter_codeforces
   :members:
   :undoc-members:
   :show-inheritance:


.. _db_select:

Select From Database
--------------------

.. automodule:: slrg_data.select
   :members:
   :undoc-members:
   :show-inheritance:


.. _combine_json:

Combine Json
------------

.. automodule:: slrg_data.combine_json
   :members:
   :undoc-members:
   :show-inheritance:


