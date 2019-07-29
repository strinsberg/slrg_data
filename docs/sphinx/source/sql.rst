SQL Examples
============

.. _big_query_sql:

BigQuery
--------

GitHub Projects
~~~~~~~~~~~~~~~

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

GitHub commits
~~~~~~~~~~~~~~

.. code-block:: sql

    #standardSQL
    SELECT
        users.id as users_id,
        users.login,
        users.company,
        users.created_at as users_created_at,
        users.type,
        users.country_code,
        users.state,
        users.city,
        users.location,
        projects.id as projects_id,
        projects.url,
        projects.name,
        projects.language,
        projects.created_at as projects_created_at,
        commits.id,
        commits.sha,
        commits.created_at
    FROM
        `ghtorrent-bq.ght.commits` commits
    INNER JOIN
        `ghtorrent-bq.ght.projects` projects
    ON
        commits.project_id = projects.id
    INNER JOIN
        `ghtorrent-bq.ght.users` users
    ON
        users.id = commits.author_id
    WHERE
        projects.deleted != true and
        users.deleted != true and
        users.fake != true and
        projects.language = 'C++';  -- Change to desired language

.. _get_results:

To get 150k random rows
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

    #standardSQL
    SELECT
        *
    FROM
        `your saved table`  -- Replace with your table's name
    ORDER BY
        RAND()
    LIMIT
        150000;  -- Adjust to the number of rows you want


.. _download_results:

To download results 10k at a time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

    #standardSQL
    SELECT
        *
    FROM
        `your saved table`  -- Replace with your table's name
    LIMIT
        10000
    OFFSET 0;

1. Run the query
2. Select 'Download as JSON'
3. Increase the OFFSET by 10,000
4. repeat until all the results are downloaded



Database
--------