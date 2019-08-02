.. _github:

Github Collection
=================

Below are walkthroughs for collecting source code samples from GitHub. They explain how to get project and commit data from GhTorrent via Google BigQuery. Then there is infomation on how to use the scripts for project and commit based collections.

More information can be found in the |github-report| of the technical report.

In order to run the scripts the :ref:`slrg_data <installation>` python package must be installed. There is also some general information on how the scripts can be run and and some information for each one :ref:`in the Scripts section <scripts>`.


.. _ght-big-query-lab:

GhTorrent and Google BigQuery
-----------------------------

.. should I include some screen shots? Also, would it be better to put some of the smaller SQL samples in line so that a person does not have to jump to them?

.. note:: You will need a Google account to be able to work with the dataset on BigQuery. You will be required to accept their terms of service and set up a project. This project is were you will be able to store tables of query results.

1. To get started open |ght-big-query| and select the red 'Compose Query' button at the top of the info panel on the right side of the screen. If the link above does not work you can access the dataset at http://ghtorrent.org/gcloud.html.

2. Under the input box for the SQL there is a row of buttons. Click the show options button on the far left. In the menu that opens unckeck the box that is titled 'use legacy sql'. You can then click the button again to hide the options.

3. Now you can query the dataset for the desired data. You should use the :ref:`example queries <big_query_sql>` and adjust the projects.language field in the where clause for the desired programming language.

4. The results of the query will appear below the SQL input area. Above the top left corner there are buttons for saving the results. If your results are larger than 10,000 rows you will not be able to download them yet.

5. To save the results of your query select the 'Save as Table' button at the top right corner of the results preview. You will be asked to select a dataset to save the table in. Select the one that you created in your initial project. Don't save it to the ght dataset.

6. Once you have the table saved you have a few options.

    1. If you want to download all the results you can query the table 10,000 rows at a time and select 'Download as JSON'. :ref:`SQL to get 10k rows at a time <download_results>`. Once you have them downloaded you can use the 

    2. If you have more results than you need you can select the saved table and query it with :ref:`SQL to get a random sample <get_results>`. Adjust the limit to get the number of rows you want. This new set of results can be saved to a table of it's own. Then follow step 1 to download them.

7. Once you have gotten the results that you want and downloaded them you must run the :ref:`Combine json script <combine_json>` to put all the results back into 1 or more data files that will be loadable by the scripts. You must run this script even if you only downloaded one file of results as they are not properly formatted for use with the scripts.

.. There should either be a short example of using the combine script here or a little more info in the script section. There will be usage info for the other scripts in this section so it might make sense. Maybe split this section into 2. one for getting results from ght and the other for what to do with those results before they can be processed by the other scripts.

When you have your desired set of GitHub project or commit data collected into data files you can follow the appropriate process below to start collecting source code samples.


.. _git-projects:

Projects Based Collection
-------------------------

To show how to use the projects based collection script I will run through an example. I will be collecting java samples from the 'java1.data'. I will assume that I have already done some collection and the script is being re-started at with the 33,000 record in the file.

..note:: The java1.data file in this example must have been collected with the :ref:`GitHub commits SQL <projects_sql>` via BigQuery.

1. Navigate to the directory that the 'java1.data' file is being stored.::

    $ cd ~/my_project/data

2. Run the collection script. I have set my login and password for both the databse and the GitHub in the configuration file.

    * From the command line::

        $ slrg-git-projects -s 33000 -l java -i java1.data

    * Or from the python interpreter::

        >>> from slrg_data import collect_git_projects
        >>> lang = 'java'
        >>> start = 33000
        >>> file = 'java1.data'
        >>> start = collect_git_projects.main(lang=lang, start=start, file=file)

    * For additional information on the available command line options and keyword parameters see the :ref:`GitHub projects script <github-projects>` description.

    * For additional information on values that can be stored in the configuration file see the :ref:`Configuration section.<config_lab>`

3. If I had not set the databse login and password I would be asked to enter them before the script started processing the data file.::

    Database Username: my_username
    Databse Password: my_password  # will not be shown when typed

4. If all the correct information is given the script will start running. You should see something like this::

    File: java1.data
    # 33004 ### {'error': 'Request limit reached'}
    No Gender: Cookizz
    Invalid project: RxJavaStackTracer ###
    # 33005 ### Processing Project: ITSLV_api ###
    # 33006 ### Api issue: Not Found
    Invalid project: juzu-example ###
    # 33007 ### No Gender: mseclab
    Invalid project: droidconit2014-symmetric-demo-step2 ###
    # 33008 ### Processing Project: lego_sumo_fighter ###
    Processing File: .... Source_code/principal.java
    -- Added
    Processing File: .... Source_code/mover.java
    -- Added
    # 33009 ### Api issue: Not Found
    Invalid project: Compilers ###


5. The script will run until a given limit of projects is processed, you press CTRL^c, or an error that cannot be recovered from is encountered. When it is finished it will display some information like this::

    ------------------------------------------------------
    File: java1.data
    Elapsed time: 4h21m13.40s
    Start=33000, Count=10000
    Total Entries Processed: 7000
    Projects successfully processed: 5172
    Files added/checked: 4500/4890 92%
    Files added/project: 4500/5172 87%

6. Restart the script to collect more records.

    * From the command line you will need to enter the same command again, but update -s to be *Start* + *Total Entries Processed*.::

        $ slrg-git-projects -s 40000 -l java -i java1.data
    
    * In the interpreter if you set the result of the main function to start you can simply run the same command again. The start variable will be updated appropriatly::

        >>> start = collect_git_projects.main(lang=lang, start=start, file=file)
        >>> start
        40000
        >>> start = collect_git_projects.main(lang=lang, start=start, file=file)

.. note:: The projects script temporarily clones repositories to validate files. This can use a lot of data.


.. _git-commits:

Commits Based Collection
------------------------

Using this script is almost identical to the projects script.

..note:: The java1.data file in this example must have been collected with the :ref:`GitHub commits SQL <commits_sql>` via BigQuery.

1. Same as projects script.

2. Same as projects, but with a different script name::

    * From the command line::

        $ slrg-git-commits -s 33000 -l java -i java1.data

    * Or from the python interpreter::

        >>> from slrg_data import collect_git_commits
        >>> lang = 'java'
        >>> start = 33000
        >>> file = 'java1.data'
        >>> start = collect_git_commits.main(lang=lang, start=start, file=file)

3. Same as projects.

4. The output will look a little different::

    pass

5. Same as projects.

6. Same as projects.


.. links

.. |ght-big-query| raw:: html

   <a href="https://bigquery.cloud.google.com/dataset/ghtorrent-bq:ght" target="_blank">GhTorrent via BigQuery</a>

.. |github-report| raw:: html

    <a href="./_static/technical_report.pdf#page=3" target="_blank">GitHub section</a>