.. _cf-collection:

Codeforces Collection
=====================

Below is a walkthrough for collecting source code samples from Codeforces. It first explains how to get a user list using the codeforces API. Then how to pre-process this user list to add things like gender or to collect a specific set of users. Finally, it explains how to run the script on a list of user records.

More information on the process can be found in the |codeforces-report| section of the technical report.

In order to run the scripts the :ref:`slrg_data <installation>` python package must be installed. There is also some general information on how the scripts can be run and and some information for each one :ref:`in the Scripts section <scripts>`.


Getting a User List
-------------------

1. Navigate to the folder you would like to store the user list in.

2. Run the script to get a list user records for all rated users from the codeforces API.::

    $ I need to make a quick script for this!!!

This will create a file called all_rated_users.data in the folder you run the script in.

Processing a User List
----------------------

Adding Gender
~~~~~~~~~~~~~

1. Navigate to the folder where the user list you want to add gender to is stored.

2. Run the :ref:`gender codeforces users <gender-codeforces>` script::

    $ slrg-gender-codeforces -i <user list filename> [other options]

The results will be a new file with all users that were able to have gender labels added. It will also produce a file of records that were unprocessed because the genderize.io API rate limit had been reached. This second file can be processed when the API has reset (see gender seciton?).

The file created by this script can be used directly with the collection script or it can be filtered further to obtain a specific set of users.

Filtering Users
~~~~~~~~~~~~~~~



Collecting Source Code Samples
------------------------------




.. |codeforces-report| raw:: html

    <a href="./_static/technical_report.pdf#page=11" target="_blank">Codeforces section</a>