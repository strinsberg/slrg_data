.. _git-collection:

Github Collection
=================

Below are walkthroughs for collecting source code samples from GitHub. They explain how to get project and commit data from GhTorrent via Google BigQuery. Then there is infomation on how to use the scripts for project and commit based collections.

More information can be found in the |github-report| of the technical report.

In order to run the scripts the :ref:`slrg_data <installation>` python package must be installed. There is also some general information on how the scripts can be run and and some information for each one :ref:`in the Scripts section <scripts>`.


.. _ght-big-query-lab:

GhTorrent and Google BigQuery
-----------------------------

.. should I include some screen shots? Also, would it be better to put some of the smaller SQL samples in line so that a person does not have to jump to them?

To collect data from the GhTorrent dataset we used BigQuery. I will go through this process below, but will not go into too much detail regarding how BigQuery works. For more information on creating projects, datasets, tables, and queries refer to the help for |big-query-classic-ui| and |big-query-new-ui|.

I used the classic ui, but it will be unavailable after 2020, so you may have to use the new ui.

.. note:: You will need a Google account to be able to work with the dataset on BigQuery. You will be required to accept their terms of service and set up a project. This project is were you will be able to store tables of query results.

1. To get started open |ght-big-query| and open a query editor for the ght dataset. If the link above does not work you can access the dataset at http://ghtorrent.org/gcloud.html.

2. Under the query editor you can open some options. Do this and unckeck the box that is titled 'use legacy sql'.

3. For this example I will query the dataset to find java projects. For other queries refer to the :ref:`SQL queries section <big_query_sql>`::

    #standardSQL
    SELECT
        users.id,
        users.login,
        users.company,
        users.created_at as users_created_at,
        users.type,
        users.country_code,
        users.state,
        users.city,
        users.location,
        projects.id as projects_id,
        projects.url as projects_url,
        projects.name as projects_name,
        projects.language as projects_language,
        projects.created_at as projects_created_at
    FROM
        `ghtorrent-bq.ght.projects` as projects
    INNER JOIN
        `ghtorrent-bq.ght.users` as users
    ON
        users.id = projects.owner_id
    WHERE
        projects.deleted != true and        -- No deleted projects
        projects.forked_from is NULL and    -- No forked projects
        users.deleted != true and           -- No deleted users
        users.fake != true and              -- No fake users
        users.country_code is not NULL and  -- Must have country
        projects.language = 'Java';         --Change to desired language

4. A preview of the results will appear below. There are options to save to CSV, JSON, and as a table. If your results are larger than 10,000 rows you will not be able to download them yet.

5. To save the results of your query select the 'Save as Table' button at the top right corner of the results preview. This will save the table in a dataset in one of your BigQuery Projects. Refer to the BigQuery help links above for instructions if you do not have a dataset set up.

6. Once you have the table saved you have a few options:

    1. If your results are too large and you want a smaller subset you can take a random sample of the data. Save the sample results to a new table and follow step 2::

        #standardSQL
        SELECT
            *
        FROM
            `my_project.my_dataset.2mill_results`  -- Replace with your table's name
        ORDER BY
            RAND()
        LIMIT
            150000;                                -- Adjust to the number of rows you want

    2. If you want to download all the results in your table you can query the table 10,000 rows at a time and select 'Download as JSON'::

        #standardSQL
        SELECT
            *
        FROM
            `my_project.my_dataset.java_projects`  -- Replace with your table's name
        LIMIT
            10000
        OFFSET 0;                       -- Increase by 10,000 until you have all results    

7. The downloaded results must be combined and formated. The :ref:`Combine json script <combine_json>` will combine all json files in a folder into 1 or more data files. These files will be formatted for processing by the scripts.

    * In the example I have downloaded 15 json files with 10,000 rows each. I want them to be in 2 data files so that I can run 2 scripts at a time. ceiling(15/2) = 8::

        $ slrg-combine-json -o java -g 8
        Combining results-20190618-152952.json
        Combining results-20190618-153054.json
        Combining results-20190618-153105.json
        Combining results-20190618-153147.json
        Combining results-20190618-153137.json
        Combining results-20190618-153030.json
        Combining results-20190618-153021.json
        Combining results-20190618-153158.json
        Combining results-20190618-153114.json
        Combining results-20190618-153126.json
        Combining results-20190618-153042.json
        Combining results-20190618-152935.json
        Combining results-20190618-152938.json
        Combining results-20190618-153008.json
        Combining results-20190618-153208.json
        ** Created java.data
        ** Created java2.data

The resulting files java1.data and java2.data are now ready to be used with the GitHub collection scripts.


.. _git-projects:

Projects Based Collection
-------------------------

To show how to use the projects based collection script I will run through an example. I will be collecting java samples from the 'java1.data'. I will assume that I have already done some collection and the script is being re-started at with the 33,000 record in the file.

.. note:: The java1.data file in this example must have been collected with the :ref:`GitHub commits SQL <projects-sql>` via BigQuery.

1. Navigate to the directory that the 'java1.data' file is being stored::

    $ cd ~/my_project/data

2. Run the collection script. I have set my login and password for both the databse and the GitHub in the configuration file.

    * From the command line::

        $ slrg-git-projects -s 33000 -l java -i java1.data

    * From the python interpreter::

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
    
    * With the interpreter if the script exits due to an unhandled exception no value will be returned. In this case you will have to manually update the start variable before re-running the script.

.. note:: The projects script temporarily clones repositories to validate files. This can use a lot of data.


.. _git-commits:

Commits Based Collection
------------------------

Using this script is almost identical to the projects script.

.. note:: The java1.data file in this example must have been collected with the :ref:`GitHub commits SQL <commits-sql>` via BigQuery.

1. Same as projects.

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

    Still Needed!!!

5. Same as projects.

6. Same as projects.


.. links

.. |ght-big-query| raw:: html

   <a href="https://bigquery.cloud.google.com/dataset/ghtorrent-bq:ght" target="_blank">GhTorrent via BigQuery</a>

.. |github-report| raw:: html

    <a href="./_static/technical_report.pdf#page=3" target="_blank">GitHub section</a>

.. |big-query-new-ui| raw:: html

    <a href="https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui" target="_blank">BigQuery new UI help</a>

.. |big-query-classic-ui| raw:: html

    <a href="https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui-classic" target="_blank">BigQuery classic UI help</a>
