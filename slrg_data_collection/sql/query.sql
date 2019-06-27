-- sql for data extraction --

-- set up server with utf8mb4 support
-- Know this will reduce the number of characters available in the length
-- to allow remote access $ sudo ufw allow mysql
-- $ systemctl start mysql
-- $ systemctl enable mysql
-- login $ mysql -u "username" -p

-- Create database
CREATE DATABASE slrg_data
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'slrg_user'@'localhost' IDENTIFIED BY 'passwd'; -- Change when run

-- Grant permissions
GRANT INSERT ON slrg_data.* TO 'slrg_user'@'localhost';
GRANT SELECT ON slrg_data.* TO 'slrg_user'@'localhost';
GRANT UPDATE ON slrg_data.* TO 'slrg_user'@'localhost';
GRANT EXECUTE ON slrg_data.* TO 'slrg_user'@'localhost';

-- create git_data table
CREATE TABLE git_data (
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


-- create cf_data table
CREATE TABLE cf_data (
  submission_id INT NOT NULL,
  source_code MEDIUMTEXT,
  programming_language TINYTEXT,
  problem_name TINYTEXT,
  difficulty INT,
  participant_type TINYTEXT,
  time TINYTEXT,
  year SMALLINT,
  month SMALLINT,
  day SMALLINT,
  handle TINYTEXT,
  first_name TINYTEXT,
  last_name TINYTEXT,
  country TINYTEXT,
  city TINYTEXT,
  organization TINYTEXT,
  contribution INT,
  user_rank TINYTEXT,
  rating INT,
  max_rank TINYTEXT,
  max_rating INT,
  registered TINYTEXT,
  PRIMARY KEY (submission_id)) 
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- create cf_refine table
CREATE TABLE cf_refine (
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

-- create git_projects table
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

-- Create table for gender
CREATE TABLE genders (
  id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
  name VARCHAR(255),
  gender VARCHAR(30),
  probability FLOAT,
  UNIQUE (name))
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Add name and gender stuff to a git_data table
ALTER TABLE git_data
ADD user_fullname TINYTEXT AFTER user_login,
ADD gender VARCHAR(30) AFTER user_fullname,
ADD gender_probability FLOAT AFTER gender;

-- Add name and gender stuff to a cf_data table
ALTER TABLE cf_data
ADD gender VARCHAR(30) AFTER last_name,
ADD gender_probability FLOAT AFTER gender;

-- GhTorrent query on bigquery
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
  users.id = commits.author_id  -- committer commits, but author makes changes
WHERE
  projects.deleted != true and
  users.deleted != true and
  users.fake != true and
  projects.language = 'C++';  -- change language for desired one


-- bigquery get a range of data
#standarSQL
SELECT
  *
FROM
  [testingforgithubdata:git_data.ght_cpp]
LIMIT 10000
OFFSET 0;  -- Sets the starting point


-- Get the sizes of our dbs in mysql
SELECT table_schema AS "Database", 
ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)" 
FROM information_schema.TABLES 
GROUP BY table_schema;

-- Get the size of all tables in the database
-- Replace slrg_data with db name
SELECT table_name AS "Table",
ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES
WHERE table_schema = "sfa-slrg_data"
ORDER BY (data_length + index_length) DESC;

-- Get a breakdown of how many users from each country in cf
-- saved mostly to remember subquery syntax
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

SELECT   country,   count(country) AS users FROM (   SELECT DISTINCT     handle,     country   FROM     cf_refine where gender_probability >= 0.8 and gender='female') AS T GROUP BY country order by users;


-- users by country in git
select
  user_country_code,
  count(user_country_code)
from (
  select distinct
    user_login,
    user_country_code
  from git_data
) as T
group by user_country_code
order by count(user_country_code);

-- samples by country and language for git
select
  user_country_code,
  count(user_country_code)
from
  git_data
where
  project_language="C++"
group by user_country_code
order by count(user_country_code);

-- find users with > a certian number of submissions where lang == ??
select
  handle,
  count(handle)
from
  cf_data
where
  programming_language='Python'
group by handle having count(handle) > 10
order by count(handle);

-- find all users with 10+ submissions and a gender probability > .9
-- change programming language for others
select
  handle,
  count(handle) as submissions
from
  (
  select
    handle
  from
    cf_data
  where gender_probability > 0.9 and programming_language='C++'
) as T
group by handle
having count(handle) >= 10
order by count(handle);

