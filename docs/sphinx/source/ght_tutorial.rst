.. _ght:

Ghtorrent dataset
-----------------

Ghtorrent is a database of GitHub metadata. We Google BigQuery to collect information from Ghtorrent on github commits and projects 

More information on Ghtorrent can be found at |ght|.

The Ghtorrent database can be accessed with Google BigQuery |ght-bigquery|.
Using BigQuery requires a google/gmail account.

More information on why and how we used Ghtorrent can be found in the
report |report-ght|. (could open to a specific page when we have a long report)


Using BigQuery
--------------

Querying Ghtorrent
~~~~~~~~~~~~~~~~~~

With the ght dataset selected click Compose Query. Then you can use an sql
query to get the data you are looking for.

To collect data for git_projects you can use SQL:

.. code-block:: sql

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
            projects.deleted != true and  -- No deleted projects
            projects.forked_from is NULL and  -- No forked projects
            users.deleted != true and  -- No deleted users
            users.fake != true and  -- No fake users
            users.country_code is not NULL and  -- Must have country
            projects.language = 'Python';  --Change to desired language

More examples can be found :ref:`here <big_query_sql>`

If you are just collecting a different language that we have already collected you can just change the 'project.language = ' statement for your desired language.

If you construct your own SQL that selects the column names in a different order, with different identifiers, or change what columns you collect you will need to change the fields variable in the configuration file (link to more instructions).

More information on colelcting github projects (link) or github commits (link).

Getting the results
~~~~~~~~~~~~~~~~~~~

BigQuery does not enable downloading more than 10000 rows of results at a time. So once you have obtained the results you are looking for you must take a few steps.

1. Select the 'save to table' option at the top right corner of the result preview.
2. Pick a dataset to save it in, give it a name and click save. (link or instructions on creating a dataset?)
3. Now you can query this table 10000 rows at a time and download those results as JSON files.

    **Example**
    
    I created a dataset called 'testingforgithubdata' with a database called 'git_data'. I stored my query results in a table called 'python_projects'.
    
    .. code-block:: sql

        #standardSQL
        SELECT
            *
        FROM
            `testingforgithubdata.git_data.python_projects`
        LIMIT
            10000  -- Only takes 10000 rows at a time
        OFFSET
            0;  -- Change this by 10000 and repeat until there are no results

4. For each query of 10000 rows before you update the offset click 'export to json' at the upper right corner of the results preview. This will download the results as a json file to your downloads folder.

Once you have downloaded as many results as you want you can proceed to combine them into larger files that will be able to be open by the scripts.

Notes
^^^^^
* It takes quite a while to process the results and get source code with the scripts. So you can download 100k or so at a time and get more as needed.
* If the results from your initail query are really large you can take a random sample and save it in a new table. Then follow the above process to get the results from the sample. :ref:`Example <get_results>`.
* If you want to take another random sample you will have to eliminate all the rows you already took first. (link to example).

Combining The JSON files
------------------------

Once you have downloaded all the results you can combine them into larger files. This will enable them to be loaded into the python scripts as well as have enough entires in each file that the scripts can run unattended for a reasonable amount of time.

Combining the files can be done with the combine_json script. If you were combining files for the git_projects you would do the following:

1. Move all the json files to 'your_project_folder/data/git_projects/json/'
2. Cd into that folder
3. Run the script
    
    Open an interpreter and run the script functions:

    >>> from slrg_data.scripts import combine_json
    >>> filename = "file_name_for_combined_json"
    >>> foldername = "folder_to_store_downloaded_json_files"
    >>> group_size = 5
    >>> combine_json.main(filename, group_size, foldername)

    Or from the command line (probably easier for this script)::

        $ combine_json

**group_size** determines how many JSON files will be combined for each data file (default is one output file).

The output files will be named '**filename**.data', 'filename2.data', etc. if there is more than one.

If **foldername** is given all JSON files will be moved to that folder. If left blank then the downloaded JSON files will be deleted.

Next Steps
~~~~~~~~~~

If you want to preprocess the data before running the collection scripts on it then goto :ref:`Pre-processing GitHub Data <git_pre>`.

Otherwise move the .data files up one folder to 'data/git_projects'. You can just skip to (link to git_projects script tutorial).


.. Links ..

.. |ght| raw:: html

        <a href="http://ghtorrent.org" target="_blank">ghtorrent.org</a>

.. |ght-bigquery| raw:: html

        <a href="https://bigquery.cloud.google.com/dataset/ghtorrent-bq:ght" target="_blank">here</a>

.. |report-ght| raw:: html

        <a href="./_static/second_draft.pdf#page=4" target="_blank">here</a>
