"""Classes and functions needed for the collection of source code
samples from GitHub.
"""
import time
import sys
import getpass
import os
import http
import random
import shutil
import hashlib

# 3rd party libraries
import git

# Local imports
from . import common
from . import script


# Git Collectors #######################################################

class GitCollector(common.Collector):
    """Base Abstract Class for GitHub collection.

    Adds 'files' and 'added' keys to the totals dict attribute
    inherited from :class:`~slrg_data.collection.common.Collector`.

    Adds methods for adding name and gender to entries.

    See :ref:`Git Collection <git-collection>` for more information
    on this part of the process.

    Attributes:
        collect_gender (bool): Wether or not to collect gender for
            entries.
        gender_wait (list): Any entries that cannot have gender assigned
            to them at the present time. Likely because the gender API
            rate limit has been reached.
        gender_file (str): A prefix for the filename for missing gender
            data to be written to.
    """

    def __init__(self, database, collection_info, log, collect_gender=True):
        super(GitCollector, self).__init__(database, collection_info, log)
        self.collect_gender = collect_gender
        self.totals.update({'files': 0, 'added': 0})
        self.gender_collector = common.GenderCollector(database, 'genders')
        self.gender_wait = []
        self.gender_file = 'missing_gender'

    def set_up(self):
        """Extends :func:`Collector.set_up() <slrg_data.collection.common.Collector.set_up>`
        to add an authenticated requests session."""
        common.Collector.set_up(self)

        login = self.collection_info.git_data.login
        passwd = self.collection_info.git_data.passwd

        self.session = authenticated_session(login, passwd)
        self.times['session'] = time.time()

    def add_name_and_gender(self, entry_data):
        """Add fullname and gender data to an entry.

        Adds 'user_fullname', 'gender' and 'gender_probability' keys
        to the entry_data dict. If any of the values are not obtainable
        they are initialized to None.

        Args:
            entry_data (dict): A row of json data gathered from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        entry_data['user_fullname'] = None
        entry_data['gender'] = None
        entry_data['gender_probability'] = None

        fullname, gender, gender_probability = self.get_fullname_and_gender(
            entry_data)

        if fullname not in [None, '']:
            if gender not in ['nil', None]:
                entry_data['user_fullname'] = fullname
                entry_data['gender'] = gender
                entry_data['gender_probability'] = gender_probability
            elif gender is None and self.collection_info.save_missing:
                print('Gender unavailable: Adding saving record ###')
                self.gender_wait.append(entry_data)
            elif gender == 'nil':
                print("No Gender: " +
                      entry_data['login'], '###')
            else:
                print("Gender API unavailable ###")

    def get_fullname_and_gender(self, entry_data):
        """Collect a github users fullname and gender data if possible.

        Args:
            entry_data(dict): A row of json data gathered from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`..

        Returns:
            (str, str, float): The fullname, gender, and
            gender_probability that can be obtained. If any of the
            values are not accessible they are returned as None.
        """
        try:
            fullname = get_fullname(
                entry_data['login'], self.session, self.times['session'])
        except RateLimitExceeded:
            wait_for_api(self.times['session'], 120, self.log.info)
            self.times['session'] = 0

        if fullname not in [None, '']:
            name = fullname.split()[0]
            gender, gender_probability = self.gender_collector.get_gender(name)
        else:
            print("No User Name: " + entry_data['login'])
            gender = None
            gender_probability = None

        return fullname, gender, gender_probability

    def write_missing(self, collection_type):
        """Run with cleanup to save any records missing gender.

        Args:
            collection_type (str): The kind of collection. projects or commits.
        """
        if self.collection_info.save_missing and self.gender_wait:
            filename = "{}_{}_{}".format(self.gender_file,
                                         self.collection_info.language,
                                         str(time.time()))
            path = os.path.join(common.SLRG_DIR, 'git',
                                collection_type, 'missing', filename)
            common.write_json_data(path, self.gender_wait)


class CommitsCollector(GitCollector):
    """Concrete Collector class for collecting source code samples using
    GitHub commit data.

    Also adds 'commits' key to the totals dict attribute inherited from
    :class:`~GitCollector`.

    See :ref:`Git Commits <git-commits>` for more information on this
    process.
    """

    def __init__(self, database, collection_info, log, collect_gender=True):
        super(CommitsCollector, self).__init__(
            database, collection_info, log, collect_gender)
        self.totals.update({'commits': 0})
        self.gender_file = 'commits_missing_gender'

    def process(self, entry):
        """Processes a row of commit data collected from GhTorrent.

        Adds necessary information and enters valid entries into the
        collectors database along with collected source code.

        Args:
            entry (dict): A row of commit data from :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        try:
            print("#", self.totals['entry'], "###", end=" ")

            commit_data = self.get_commit_data(entry['url'], entry['sha'])

            if api_ok(commit_data, write=self.log.info):
                self.process_commit(commit_data, entry)

        except RateLimitExceeded:
            wait_for_api(self.times['session'], 120, self.log.info)
            self.times['session'] = time.time()
        except KeyError as error:
            self.log.error("In process:", error)

    def get_commit_data(self, project_url, commit_sha):
        """Requests the commit data for a commit from the Github API.

        Args:
            project_url (str): The api url for the commit's project.
            commit_sha (str): The unique hash that identifies the
                desired commit on github.

        Returns:
            (dict): A dict with the response for the API. See
                https://developer.github.com/v3/repos/commits/
                for more info.
        """
        url = project_url + "/commits/" + commit_sha
        return common.session_get_json(self.session, url)

    def process_commit(self, commit_data, entry):
        """Collects additional data and adds valid commits to the
        database.

        Args:
            commit_data (dict): A GitHub API response for commit
                information.
            entry (dict): A row of commit data from :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        if self.collect_gender:
            self.add_name_and_gender(entry)
            if (entry['user_fullname'] is None
                    or entry['gender'] is None):
                return

        self.totals['commits'] += 1
        print("Processing Commit:", commit_data['sha'], "###")

        for file_data in commit_data['files']:
            self.totals['files'] += 1

            if not self.is_valid(file_data):
                continue

            print("Processing File:", file_data['filename'], "....")
            if self.add_file_to_db(file_data, entry):
                self.totals['added'] += 1
                print("-- Added")

    def is_valid(self, file_data):
        """Confirms a file meets the requirements to be added to the
        database.

        See :ref:`Git Commits <git-commits>` for more information on
        what makes a file valid.

        Args:
            file_data (dict): The number of 'changes', 'status', and 'filename'     of the file being processed.

        Returns:
            bool: True if the file meets the requirements, otherwise
                False. 
        """
        try:
            changes = int(file_data['changes'])
            if changes < 10 or file_data['status'] != 'added':
                return False

            return has_extensions(file_data["filename"],
                                  self.collection_info.validation.extensions)

        except KeyError as error:
            self.log.error("In is_valid", error)
            return False

    def add_file_to_db(self, file_data, entry):
        """Attempts to add all necessary information for a source code
        sample to the database.

        Args:
            file_data (dict): The number of 'changes', 'status',
                'filename', and source code 'patch' of the file being
                processed.
            entry (dict): A row of commit data from :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.

        Returns:
            bool: True if the information was successfully added to
                the database, otherwise False.
        """
        values = self.get_entry_values(entry)
        values.extend(self.get_file_values(file_data))

        if self.database.insert(self.collection_info.table.columns,
                                self.collection_info.table.name, values):
            return True
        return False

    def transform_entry_value(self, value, entry_field):
        """Transforms commit creation time into a string.

        Overrides
        :func:`~slrg_data.collection.common.Collector.transform_entry_value`.

        Args:
            value (any): The value to transform if needed.
            entry_field (str): The field that the value came from
                in the entry. Required to know which values to
                transform.
        """
        v = value
        if v is not None and entry_field.find('created') > -1:
            v = common.get_time_string(float(v))
        return v

    def get_file_values(self, file_data):
        """Returns file_data values in the proper order to add to the
        database.

        Args:
            file_data (dict): The number of 'changes', 'status',
                'filename', and source code 'patch' of the file being
                processed.

        Returns:
            (tuple): Values of file sha, filename, source code, and number of
                changes made.
        """
        source = self.clean_source(file_data['patch'])
        return (file_data['sha'], file_data['filename'], source,
                file_data['changes'])

    def clean_source(self, source):
        """Remove extra commit information from the source code.

        Args:
            source (str): File data 'patch' contents with extra + chars
                on every line and a header line indicating the number
                of changes.
        """
        rm_plus = source.replace("\n+", "\n")
        start = source.find("\n")
        return rm_plus[start + 1:]

    def clean_up(self):
        """Prints details of the collection for commits, files processed,
        and files added.

        Extends :func:`GitCollector.clean_up() <GitCollector.clean_up>`.
        """
        super(CommitsCollector, self).clean_up()

        commits = self.totals['commits'] + 0.1
        self.log.info("Commits successfully processed: {:.0f}".format(commits))

        added = self.totals['added']
        files = self.totals['files'] + 0.1
        self.log.info("Files added/checked: {}/{:.0f} {:.0f}%".format(
            added, files, (added / files) * 100))
        self.log.info("Files added/commit: {}/{:.0f} {:.0f}%".format(
            added, commits, (added / commits) * 100))

        self.write_missing('commits')


class ProjectsCollector(GitCollector):
    """Concrete Collector class for collecting source code samples using
    GitHub project data.

    Also adds 'projects' key to the totals dict attribute inherited from
    :class:`~GitCollector`.

    see :ref:`Git Projects <git-projects>` for more information on this process.
    """

    def __init__(self, database, collection_info, log, collect_gender=True):
        super(ProjectsCollector, self).__init__(
            database, collection_info, log, collect_gender)
        self.totals.update({'projects': 0})
        self.gender_file = 'projects_missing_gender'

    def process(self, project_data):
        """Collects additional data and adds valid projects to the
        database.

        Args:
            project_data (dict): A row of project data from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        print("#", self.idx, "###", end=" ")

        # Don't want to continue if the name or gender are not found
        if self.collect_gender:
            self.add_name_and_gender(project_data)
            if (project_data['user_fullname'] is None
                    or project_data['gender'] is None):
                print("Invalid project: " + project_data['name'] + " ###")
                return

        self.add_contributors(project_data)
        if not self.is_valid_project(project_data):
            print("Invalid project: " + project_data['name'] + " ###")
            return

        self.totals['projects'] += 1
        print("Processing Project:", project_data['name'], "###")

        self.process_valid_project(project_data)

    def is_valid_project(self, project_data):
        """Checks to make sure project is valid.

        See :ref:`Git Projects <git-projects>` for more information on what make a
        project valid.

        Args:
            project_data (dict): A row of project data from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.

        Returns:
            bool: True if the project is valid, False otherwise.
        """
        contribs = project_data['contributors']
        if contribs is None:
            return False
        if len(contribs) > 1:
            print("Invalid number of contributors:", len(contribs))
            return False

        if (len(contribs) == 1
                and project_data['login'] != contribs[0]['author']['login']):
            return False

        return True

    def process_valid_project(self, project_data):
        """Clones the project repo and adds all valid source code to
        the database.

        Args:
            project_data (dict): A row of project data from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        repo_path = None
        try:
            repo, repo_path = self._make_repo(project_data)
            files = get_single_author_files(repo, repo_path,
                                            self.collection_info.validation,
                                            project_data["user_fullname"],
                                            project_data["login"])

            for filename in files:
                path = os.path.join(repo_path, filename)
                self.process_file(path, filename, project_data)

        except git.GitError as error:
            self.log.error("In process", error)

        finally:
            try:
                shutil.rmtree(repo_path)
            except (FileNotFoundError, TypeError):
                pass

    def _make_repo(self, project_data):
        """Clones a repository and return a git.Repo object for it."""
        repos_dir = os.path.join(common.SLRG_DIR, 'git/projects/temp_repos')
        temp_dir = "temp_{}".format(str(random.randint(0, 2000000)))
        repo_path = os.path.join(repos_dir, temp_dir)

        url = "https://:@github.com/{}/{}.git".format(
            project_data['login'], project_data['name'])

        repo = git.Repo.clone_from(url, repo_path)
        return repo, repo_path

    def add_contributors(self, project_data):
        """Add a list of contributors to project data.

        Args:
            project_data (dict): A row of project data from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        project_data['contributors'] = None
        contrib_url = "{}/stats/contributors".format(project_data['url'])
        contribs = common.session_get_json(self.session, contrib_url)

        try:
            if api_ok(contribs, write=self.log.info):
                project_data['contributors'] = contribs

        except RateLimitExceeded:
            wait_for_api(self.times['session'], 120, self.log.info)
            self.times['session'] = time.time()

    def process_file(self, path, filename, project_data):
        """Process a file and add it to the database if it is valid.

        Args:
            path (str): The full path to the file.
            filename (str): The files path in the repository.
            project_data (dict): A row of project data from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.
        """
        self.totals['files'] += 1
        file_data = self.get_file_data(path, filename)

        if file_data is not None:
            print("Processing File:", "....", filename)

            if self.add_file_to_db(file_data, project_data):
                print("-- Added")
                self.totals['added'] += 1

    def get_file_data(self, path, filename):
        """Collects the source and other file info from the file.

        In addition to the source code a count of the number of lines
        in the file is determined and a hash of the filename is created.

        Args:
            path (str): The full path to the file.
            filename (str): The files path in the repository.

        Returns:
            list: If the file is valid returns a list with the hash of
                the filename, the filename, the source code, and a
                line count. If the file is not valid returns None.
        """
        try:
            with open(path) as file:
                source = file.read()
        except (FileExistsError, FileNotFoundError,
                UnicodeDecodeError) as error:
            self.log.error("File Error", error)
            return None

        line_count = source.count('\n')
        if self.is_valid_file(filename, source, line_count):
            hash_name = hashlib.md5(filename.encode()).hexdigest()
            return [hash_name, filename, source, line_count]

        print("Lines out of range: " + str(line_count))
        return None

    def is_valid_file(self, filename, source, line_count):
        """Checks to see if a file is valid.

        Additional validation of a file. Currently only checks to make
        sure the number of lines is the range [10, 1000]

        Args:
            filename (str): The files path in the repository.
            source (str): The source code from the file.
            line_count (int): The number of lines in the source.

        Returns:
            bool: True if the file is valid, otherwise False.
        """
        if 10 <= line_count <= 1000:
            return True
        return False

    def add_file_to_db(self, file_data, project_data):
        """Attempts to add all necessary information for a source code
        sample to the database.

        Args:
            file_data (dict): The number of 'changes', 'status',
                'filename', and source code 'patch' of the file being
                processed.
            project_data (dict): A row of project data from
                :ref:`GhTorrent via BigQuery <ght-big-query-lab>`.

        Returns:
            bool: True if the information was successfully added to
                the database, otherwise False.
        """
        values = self.get_entry_values(project_data)
        values.extend(file_data)

        if self.database.insert(self.collection_info.table.columns,
                                self.collection_info.table.name, values):
            return True
        return False

    def clean_up(self):
        """Prints details of the collection for projects, files processed,
        and files added.

        Extends :func:`GitCollector.clean_up() <GitCollector.clean_up>`.
        """
        super(ProjectsCollector, self).clean_up()

        projects = self.totals['projects'] + 0.1
        self.log.info(
            "Projects successfully processed: {:.0f}".format(projects))

        added = self.totals['added']
        files = self.totals['files'] + 0.1
        self.log.info("Files added/checked: {}/{:.0f} {:.0f}%".format(
            added, files, (added / files) * 100))
        self.log.info("Files added/project: {}/{:.0f} {:.0f}%".format(
            added, projects, (added / projects) * 100))

        self.write_missing('projects')


class GitCollectionInfo(common.CollectionInfo):
    """Information required for collecting source from github.

    Attributes:
        git_data (GithubData): Login and password info for a git account.
        language (str): The language of the data being collected.
    """

    def __init__(self, records, table, validation, limits, git_data, lang,
                 save_missing):
        super(GitCollectionInfo, self).__init__(
            records, table, validation, limits)
        self.git_data = git_data
        self.language = lang
        self.save_missing = save_missing


class GithubData:
    """Login information for a git account.

    Attributes:
        login (str): A git login name.
        passwd (str): A git password.

    """

    def __init__(self, login, passwd):
        self.login = login
        self.passwd = passwd


class SingleAuthorFilter:
    """Helper class to collect file paths for all the single author files
    in a repo.

    Attributes:
        repo (git.Repo): The repository object.
        repo_path (str): The full path to the locally cloned repo.
        validation (ValidationData): Information to determine if a file
            is of the right type and not to be excluded.
        name (str): The repository author's name.
        login (str): The repository author's login.
    """

    def __init__(self, repo, repo_path, validation, name, login):
        self.repo = repo
        self.repo_path = repo_path
        self.validation = validation
        self.name = name
        self.login = login

    def get_valid_files(self, full_path, relative_path):
        """Recursively gets all the file paths in a repo that are valid.

        See :ref:`Git Projects <git-projects>` for more info on what
        makes a file valid.

        Args:
            full_path (str): The full path of a file or directory on the
                local machine.
            relative_path (str): The path of the file or folder in the
                repository.

        Returns:
            list: A list of relative file paths that are valid.
        """
        files = []
        try:
            with os.scandir(full_path) as it:
                for entry in it:

                    if entry.is_file():
                        if self.is_valid_file(entry.name):
                            path = os.path.join(
                                relative_path, entry.name)
                            count_data = self.get_blame_count(path)
                            if len(count_data) == 1 and (
                                    self.name in count_data
                                    or self.login in count_data):
                                files.append(path)

                    else:
                        if not self.is_excluded_dir(entry.name):
                            relative_path = os.path.join(
                                relative_path, entry.name)
                            files.extend(
                                self.get_valid_files(entry.path, relative_path))

        except FileNotFoundError as error:
            print("File not found (_SingleAuthorFiles): ", error)

        return files

    def is_valid_file(self, filename):
        """Checks if a filename has the right extension and is not an
        excluded file.

        Args:
            filename (str): The file's name (not a full or relative path).

        Returns:
            bool: True if the filename is valid, otherwise False.
        """
        if filename in self.validation.exclude_files:
            return False
        return has_extensions(filename, self.validation.extensions)

    def is_excluded_dir(self, dirname):
        """Checks if a directory name is not in the list of excluded
        directories.

        Args:
            dirname (str): The directory's name
                (not a full or relative path).

        Returns:
            bool: True if the directory is in the excluded list,
                otherwise False.
        """
        if dirname in self.validation.exclude_dirs:
            return True
        return False

    def get_blame_count(self, path):
        """Returns a dictionary of contributors on a file and the number
        of contributions they made.

        Args:
            path (str): The relative path of the file in the repository.

        Returns:
            dict: A dict with names/logins of contributors and a count
                of the number of contributions they made to the file.
        """
        count = {}
        try:
            for commit, _ in self.repo.blame(None, path):
                if commit.author in count:
                    count[commit.author.name] += 1
                else:
                    count[commit.author.name] = 1
        except (git.exc.GitError, KeyError):  # pylint: disable=no-member
            pass
        return count

# Functions ############################################################


def authenticated_session(name=None, passwd=None):
    """Create an authenticated requests session for interacting with the
    github api.

    If either are None then the user will be asked to input them.

    Args:
        name (str): A git login name.
        passwd (str): A git password.
    """
    name = input("Git username: ") if name is None else name
    prompt = "Github Password: "
    return common.requests_session(name, passwd, prompt)


def wait_for_api(session_time, padding, write=print):
    """Sleeps a program until the git api rate limit resets.

    Args:
        session_time (int): The timestamp of the time the api was last
            reset, or when the program started.
        padding (int): Extra time to add to the sleep to make sure it
            does not start too early.
        write (func): A function to write the sleep information. Default
            is print.
    """
    now = time.time()
    elapsed = now - session_time
    if elapsed > 3600:
        elapsed = elapsed % 3600
    sleep_seconds = 3600 - elapsed + padding

    sleep_time = common.find_time(sleep_seconds)

    write('**** Waiting for github api reset: {} ****'.format(sleep_time))
    write('Elapsed: {}, Current time: {}, Sleeping until: {}'.format(
        common.find_time(elapsed), common.get_time_string(now),
        common.get_time_string(now + sleep_seconds)))

    time.sleep(sleep_seconds)
    write('Slept for: {}'.format(sleep_time))


def api_ok(response, write=print):
    """Tests a GitHub API response for errors.

    Args:
        response (dict): A json response from the GitHub API.
        write (func): A function to write any api information.
            Default is print.

    Returns:
        bool: True if there is no issue with the response, otherwise
            False.

    Raises:
        RateLimitExceeded: If the GitHub API rate limit has been
            exceeded.
        ScriptInputError: If the response indicates that login or
            password information is incorrect.
        GitApiError: If the response returns any other kind of error
            that cannot be ignored.
    """
    if response is None:
        return False
    if 'message' in response:
        write("Api issue: {}".format(response['message']))

        if response['message'].find('rate limit exceeded') > -1:
            raise RateLimitExceeded("Github RateLimit Exceeded")
        elif response['message'] == 'Server Error':
            time.sleep(10)
            return False
        elif response['message'] == 'Bad credentials':
            raise script.ScriptInputError(
                "Input Error: Incorrect github username or password")
        elif (response['message'].find('No commit found for SHA') > -1
                or response['message'] in
                ['Not Found', 'Repository access blocked']):
            return False

        write("Git api Error: " + str(response))
        raise GitApiError(str(response))

    return True


def has_extensions(filename, extensions):
    """Checks to see if a filename ends with one of the given extensions.

    Args:
        filename (str): A filename or path.
        extensions (list): A list of extensions to check for.

    Returns:
        bool: True if the filename ends with one of the extensions,
            False if it ends with none of them.
    """
    for ext in extensions:
        if filename.endswith(ext):
            return True
    return False


def get_fullname(login, request_session, session_time):
    """Get a fullname for a github user login.

    Args:
        login (str): The git account login name.
        request_session: An github authenticated requests session object.
        session_time (int): A timestamp of the time of the last GitHub
            API reset or the start of the program.

    Returns:
        str: The fullname of the GitHub user, or None if it cannot be
            obtained.

    Raises:
        RateLimitExceeded: If the GitHub API rate limit has been
            exceeded.
    """
    url = "https://api.github.com/users/" + login
    data = common.session_get_json(request_session, url)

    try:
        if data is not None and 'name' in data and api_ok(data, session_time):
            return data['name']
    except RateLimitExceeded as limit:
        raise limit
    except GitApiError:
        pass

    return None


def get_single_author_files(repo, repo_path, validation, name, login):
    """Returns a list of relative filepaths for all valid single author
    files in a git repository.

    Args:
        repo (git.Repo): The repository object.
        repo_path (str): The full path to the locally cloned repo.
        validation (ValidationData): Information to determine if a file
            is of the right type and not to be excluded.
        name (str): The repository author's name.
        login (str): The repository author's login.

    Returns:
        list: A list of relative file paths that are valid.
    """
    file_filter = SingleAuthorFilter(repo, repo_path, validation, name, login)
    try:
        return file_filter.get_valid_files(repo_path, "")

    except OSError as error:
        print("OSError (_SingleAuthorFiles):", error)
        return []


# Exceptions ###########################################################

class GitApiError(Exception):
    """Error for fatal GitHub Api errors."""


class RateLimitExceeded(GitApiError):
    """Error for GitHub Api rate limit reached."""
