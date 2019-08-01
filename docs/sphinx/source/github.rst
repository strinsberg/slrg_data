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

When you have your desired set of GitHub project or commit data collected into data files you can follow the apporpriate process below to start collecting source code samples.



.. _git-projects:

Projects Based Collection
-------------------------

1. Navigate to the directory that the processed data files from BigQuery are stored.

2. Run the  with the desired data file as the argument to the -i option. Additional information on the available command line options is available with the :ref:`GitHub projects script <github-projects>` description.::

    $ slrg-git-projects -i <filename> [other options]

3. Some information is required for the script to run. If an option is not given at the command line or set in the :ref:`configuration file <config_lab>` you will be asked for it. For example git account name and password.

4. Once all the information is given the script will start running. You should see something like this::

    # 68207 ### Processing Project: MMDevBase ###
    # 68208 ### Invalid project: NettyBook ###
    # 68209 ### Invalid project: Dagger2Demo ###
    # 68210 ### Gender nil: yangboz
    Invalid project: fuzzy-boo ###
    # 68211 ### Processing Project: tbc-ticket-dispenser-java ###
    Processing File: .... td/src/main/java/kata/td/TicketDispenser.java
    -- Added
    Processing File: .... td/src/main/java/kata/td/TurnNumberSequence.java
    -- Added
    Processing File: .... td/src/main/java/kata/td/TurnTicket.java
    -- Added
    # 68212 ### Invalid project: adblock_plus_ ###

The script will run until a given limit of projects is processed, you press CTRL^c, or an error that cannot be recovered from is encountered. When it is finished it will display some information like this::

    ------------------------------------------------------
    File: java.data
    Elapsed time: 2h53m13.40s
    Start=64100, Count=10000
    Total Entries Processed: 4422
    Projects successfully processed: 2172
    Files added/checked: 1820/1935 94%
    Files added/project: 1820/2172 84%

The most important items are *Start* and *Total Entries Processed*. *Start* tells you what entry processing started on. If you start the script again the value of *Start* should be *Start + Total Entries Processed*. If the script was run as a function in the Python3 interpreter then this value is returned by the funtion.

.. note:: The projects script temporarily clones repositories to validate files. This can use a lot of data.



.. _git-commits:

Commits Based Collection
------------------------

Using this script is almost identical to the projects script.

1. Navigate to the directory that the processed data files from BigQuery are stored.

2. Run the  with the desired data file as the argument to the -i option. See :ref:`GitHub commits script <github-commits>` for more info.::

    $ slrg-git-commits -i <filename> [other options]

3. Once all the information is given the script will start running. You should see something like this::

    # 68207 ### Processing Project: MMDevBase ###
    # 68208 ### Invalid project: NettyBook ###
    # 68209 ### Invalid project: Dagger2Demo ###
    # 68210 ### Gender nil: yangboz
    Invalid project: fuzzy-boo ###
    # 68211 ### Processing Project: tbc-ticket-dispenser-java ###
    Processing File: .... td/src/main/java/kata/td/TicketDispenser.java
    -- Added
    Processing File: .... td/src/main/java/kata/td/TurnNumberSequence.java
    -- Added
    Processing File: .... td/src/main/java/kata/td/TurnTicket.java
    -- Added
    # 68212 ### Invalid project: adblock_plus_ ###

When finished the script displays the same information as the projects script.


.. links

.. |ght-big-query| raw:: html

   <a href="https://bigquery.cloud.google.com/dataset/ghtorrent-bq:ght" target="_blank">GhTorrent via BigQuery</a>

.. |github-report| raw:: html

    <a href="./_static/technical_report.pdf#page=3" target="_blank">GitHub section</a>