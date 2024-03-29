.. _cf-collection:

Codeforces Collection
=====================

Below is an example for collecting source code samples from Codeforces. It first explains how to get a user list using the codeforces API. Then how to pre-process this user list to add things like gender or to collect a specific set of users. Finally, it explains how to run the script on a list of user records.

More information on the process can be found in the |codeforces-report| section of the technical report.

In order to run the scripts the slrg_data package :ref:`must be installed <installation>` first. There is also some general information on how the scripts can be run and and some information for each one :ref:`in the Scripts section <scripts>`.


Getting a User List
-------------------

1. Navigate to the folder you would like to store the user list in.

2. Run the script to get a list user records for all rated users from the codeforces API.::

    $ slrg-cf_users
    User list created: cf_rated_users.json

Processing a User List
----------------------

Processing the user list is necessary to obtain a list of user records that will
load with pythons json library. It is also good to select a specific set of
users before collecting source code.

There are 2 scripts to do this. One to add genders to a group of users and one
to filter out a specific set of users.

Due to rate limiting it can be best to filter
out a smaller set of users before adding gender. Then filtering those users
again if needed, such as when looking for only users with a gender probability
above a certain threshold.

**See** :ref:`Gender <gender_collection>` for more info on rate limiting and a link to the gender section in the technical report.

Adding Gender
~~~~~~~~~~~~~

1. Navigate to the folder where the 'cf_rated_users.json' file is being stored::

    $ cd ~/my_project/data

2. Run the :ref:`slrg-gender-codeforces <gender-cf>` script. I am assuming that the database information is set in the configuration file and that output files will use default names::

    $ slrg-gender-codeforces -i cf_rated_users.json

Two files will be created

* gender.data
    Contains all the users that could be gendered.
* missing_gender.data
    Contains any users that gender information was unavailable because the genderize.io API rate limit had been reached. When the limit resets you can run the script again with this file as the input file.

The file created by this script can be used directly with the collection script or it can be filtered further to obtain a more specific set of users.

Filtering Users
~~~~~~~~~~~~~~~

If you want to collect a certain group of users you can filter the user list with the :ref:`slrg-filter-codeforces script <filter-cf>`. The script provides options for common filtering categories. For more advanced filtering you may need to write your own script.

1. Navigate to the folder with the user list.

2. Run the script with the appropriate filters. Here I am trying to get only female users with a gender probability of 0.8 or higher from Canada and Russia::

    $ slrg-filter-codeforces -i gendered.data -o can_rus_female.data --country='canada russia' --gender=female --gen_prob=0.8

This will create the file 'can_rus_female.data'. It will contain a list of records for users that meet these requirements. 

Collecting Source Code Samples
------------------------------

1. Navigate to the folder containing the user list you want to collect source code samples from. The user list file can be any file generated by one of the above scripts.

2. Run the collection script. I have set my databse login information and programing language information in the configuration file.

    * From the command line::

        $ slrg-collect-codeforces -i can_rus_female.data -s 1
    
    * With the Python interpreter::

        >>> from slrg_data import collect_codeforces
        >>> start = 1
        >>> file = 'can_rus_female.data'
        >>> start = collect_codeforces.main(start=start, file=file)

    * For additional information on the available command line options and keyword parameters see the :ref:`Codeforces script <codeforces-collection>` description.

    * For additional information on values that can be stored in the configuration file see the :ref:`Configuration section.<config_lab>`

3. If I had not set the databse login and password I would be asked to enter them before the script started processing the data file.::

    Database Username: my_username
    Databse Password: my_password  # will not be shown when typed

4. If all the correct information is given the script will start running. The script uses the Selenium web driver and will open a web browser to use for the collection. While the script runs this web browser will load pages and open submission source code popups. In the command line you will see something like this::

    File: can_rus_female.data
    ## 0 ## User: BrainDeveloper ####
    -- Received Submissions
    -- Already had subs: 0
    Processing submission: 1322805 Matchmaker
    -- 1 -- Added: Matchmaker
    Processing submission: 1321627 Friends or Not
    -- 2 -- Added: Friends or Not
    Processing submission: 1297393 Unlucky Ticket
    -- 3 -- Added: Unlucky Ticket
    Processing submission: 1295665 Twins
    -- 4 -- Added: Twins
    Processing submission: 924452 Turing Tape
    -- 5 -- Added: Turing Tape
    Processing submission: 921397 Unary

5. The script will run until a given limit of projects is processed, you press CTRL^c, or an error that cannot be recovered from is encountered. It will also end with an error if you interact with the web browser. When it is finished it will display some information like this::

    ------------------------------------------------------
    File: can_rus_female.data
    Elapsed time: 0h1m35.75s
    Start=43, Count=100
    Total Entries Processed: 1
    Users successfully processed: 1
    Submissions added/checked 5/26 19%

6. Restart the script to collect more records.

    * From the command line you will need to enter the same command again, but update -s to be *Start* + *Total Entries Processed*.::

        $ slrg-collect-codeforces -i can_rus_female.data -s 44
    
    * In the interpreter if you set the result of the main function to start you can simply run the same command again. The start variable will be updated appropriatly::

        >>> start = collect_codeforce.main(start=start, file=file)
        >>> start
        44
        >>> start = collect_codeforces.main(start=start, file=file)
    
    * With the interpreter if the script exits due to an unhandled exception no value will be returned. In this case you will have to manually update the start variable before re-running the script.

.. note:: The script will only attempt to process the most recent 50 submissions for a user. Usually it is successful in collecting 15-30 submissions. If you want more submissions from a user the best thing to do is wait and run the script again once the users have solved more problems. The collection class could be modified to collect more submissions, but this modification is beyond the scope of this documentation.

.. |codeforces-report| raw:: html

    <a href="./_static/technical_report.pdf#page=21" target="_blank">Codeforces section</a>