SQL Examples
============

.. _big_query_sql:

BigQuery
--------

.. _projects-sql:

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

.. _commits-sql:

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

Git Projects
~~~~~~~~~~~~

.. code-block:: sql

    CREATE TABLE git_projects (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        user_login TINYTEXT,
        user_fullname TINYTEXT,
        gender VARCHAR(30),
        gender_probability FLOAT,
        user_company TINYTEXT,
        user_created TINYTEXT,  
        user_type TINYTEXT,
        user_country_code TINYTEXT,
        user_state TINYTEXT, 
        user_city TINYTEXT,
        user_location TINYTEXT,
        project_id INT NOT NULL, 
        project_url TEXT,
        project_name TINYTEXT,
        project_language TINYTEXT, 
        project_created TINYTEXT,
        file_hash VARCHAR(255) NOT NULL,
        file_name TINYTEXT,
        file_contents MEDIUMTEXT,
        file_lines INT,
        UNIQUE (project_id, file_hash)) 
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;


Git Commits
~~~~~~~~~~~

.. code-block:: sql

    CREATE TABLE git_commits (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        user_login TINYTEXT,
        user_company TINYTEXT,
        user_created TINYTEXT,  
        user_type TINYTEXT,
        user_country_code TINYTEXT,
        user_state TINYTEXT, 
        user_city TINYTEXT,
        user_location TINYTEXT,
        project_id INT NOT NULL, 
        project_url TEXT,
        project_name TINYTEXT,
        project_language TINYTEXT, 
        project_created TINYTEXT,
        commit_id INT,
        commit_sha TINYTEXT, 
        commit_created TINYTEXT,
        file_sha VARCHAR(200) NOT NULL,
        file_name TINYTEXT,
        file_contents MEDIUMTEXT,
        file_changes INT,
        UNIQUE (project_id, file_sha)) 
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

Codeforces
~~~~~~~~~~

.. code-block:: sql

    CREATE TABLE cf_data (
        submission_id INT NOT NULL,
        source_code MEDIUMTEXT not null,
        programming_language varchar(50) not null,
        problem_name VARCHAR(255) NOT NULL,
        difficulty INT,
        participant_type TINYTEXT,
        time TINYTEXT,
        year SMALLINT,
        month SMALLINT,
        day SMALLINT,
        handle VARCHAR(255) NOT NULL,
        first_name TINYTEXT not null,
        last_name TINYTEXT,
        gender VARCHAR(30) not null,
        gender_probability FLOAT,
        country TINYTEXT not null,
        city TINYTEXT,
        organization TINYTEXT,
        contribution INT,
        user_rank TINYTEXT not null,
        rating INT not null,
        max_rank TINYTEXT,
        max_rating INT,
        registered TINYTEXT,
        PRIMARY KEY (submission_id),
        UNIQUE (handle, problem_name))
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

