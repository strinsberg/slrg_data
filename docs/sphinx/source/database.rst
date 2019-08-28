Database
========

Our database is stored by the University of Lethbridge. It is a MySQL8 server. More information on MySQL8 can be found at https://dev.mysql.com/doc/refman/8.0/en/.

Some more information may be available in the |database-report| of the technical
report.

Host Name
    :code:`mysql-8-p.uleth.ca`

Database Name
    :code:`sfa-slrg_data`

.. note:: You can connect only connect to the database from on the Uleth network (not the guest wifi).

.. note:: If you need an account for the database contact IT with the above information to request a login. You should only need SELECT and INSERT privileges, unless you are going to be adding new tables. Please mention that you are working with Dr. Rice.

For interacting with the database using the mysql command line client can be effective for simple stuff. Info at https://dev.mysql.com/doc/refman/8.0/en/mysql.html. It is probably better to use something like MySQL Workbench for more complicated things. Info at https://www.mysql.com/products/workbench/.


Available Tables and Schemas
----------------------------

There are currently 4 sets of tables. Our schemas are generated for simplicity and not very memory efficiency.

GitHub Projects Tables
    * C++ samples :code:`git_projects_cpp`
    * Python samples :code:`git_projects_python`
    * Java samples :code:`git_projects_java`

    Put in schema

GitHub Commits Tables
    * C++ samples :code:`git_commits_cpp`
    * Python samples :code:`git_commits_python`
    * Java samples :code:`git_commits_java`

    Put in schema

Codeforces Table
    * C++, Python, Java samples :code:`cf_data`

    Put in schema

Gender Table
    * First names with gender :code:`genders`

    Put in schema

Table Creation SQL
------------------

Here are a few SQL queries used to create our tables. If you are creating new tables to run with the scripts you should use these. Probably you will only need to modify the table name.

Create git_projects table
    .. code-block:: sql

        CREATE TABLE git_projects (  -- Modify table name if needed
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

Create git_commit tables
    .. code-block:: sql

        CREATE TABLE git_commits_cpp (  -- Modify table name if needed
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

Create cf_data table
    .. code-block:: sql

        CREATE TABLE cf_refine (  -- Modify table name if needed
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

Create table for gender
    .. code-block:: sql

        CREATE TABLE genders (
        id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
            name VARCHAR(255),
            gender VARCHAR(30),
            probability FLOAT,
            UNIQUE (name))
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci;


Example Queries For Our Database
--------------------------------

I have provided some sample queries for quick examination of groups in the database. If you are going to work with a subset of the data it is often easier to collect all the submissions that fit into the general categories you want and filter them further with Python or R when you work with them.

The :ref:`slrg-select script <db_select>` can be used to run a query and store the results in a json or csv file. This can be preferable to using the mysql command line to get your data out of the database. However, for more complicated work it may be easier with MySQL Workbench.

Get number of users for each country
    * Codeforces

    .. code-block:: sql

        SELECT
            country,
            count(country) AS users
        FROM (
            SELECT DISTINCT
                handle,
                country
            FROM
                cf_data
        ) AS T
        GROUP BY country;
    
    * GitHub -- Works for all commit and projects tables
    
    .. code-block:: sql

        SELECT
            user_country_code,
            count(user_country_code)
        FROM (
            SELECT DISTINCT
                user_login,
                user_country_code
            FROM
                git_commits_cpp  -- Change as needed
        ) as T
        GROUP BY user_country_code
        ORDER BY count(user_country_code);
    
Get users and number of samples
    * Codeforces

    .. code-block:: sql

        SELECT
            handle,
            count(handle) as samples
        FROM
            cf_data
        GROUP BY handle
        ORDER BY count(handle);

    * GitHub

    .. code-block:: sql

        SELECT
            user_login,
            count(user_login) as samples
        FROM
            git_projects_java  -- Change as needed
        GROUP BY user_login
        ORDER BY count(user_login);

User and number of file lines from GitHub projects
    .. code-block:: sql

        SELECT
            user_login,
            sum(file_lines) as lines  -- Change file_lines to file_changes for commits tables
        FROM
            git_projects_java         -- Change as needed
        GROUP BY user_login
        HAVING sum(file_lines) >= 300
        ORDER BY sum(file_lines);


.. _big_query_sql:

SQL For GhTorrent and Google BigQuery
-------------------------------------

.. _projects-sql:

GitHub Projects
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


.. |database-report| raw:: html

    <a href="./_static/technical_report.pdf#page=34" target="_blank">Database section</a>