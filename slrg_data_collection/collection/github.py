"""Collectors and other github collection related functions to support
collecting source code from github.
"""
import time
import sys
import getpass
import os
import http
import random
import shutil
import hashlib

import git

from . import common


class ProjectsCollector(common.Collector):
    """Extracts source code from single contributor github projects."""

    def __init__(self, database, collection_info, log):
        common.Collector.__init__(self, database, collection_info, log)
        self.totals.update({'projects': 0, 'files': 0, 'added': 0})
        self.gender_wait = []

    def set_up(self):
        """Creates session and set its credentials."""
        common.Collector.set_up(self)

        login = self.collection_info.git_data.login
        passwd = self.collection_info.git_data.passwd

        self.session = authenticated_session(login, passwd)
        self.times['session'] = time.time()

    def process(self, project_data):
        """Process a github project."""
        print("#", self.idx, "###", end=" ")

        self.add_name_and_gender(project_data)
        self.add_contributors(project_data)

        if not self.is_valid_project(project_data):
            self.log.info("Invalid project: " + project_data['name'] + " ###")
            return

        self.totals['projects'] += 1
        print("Processing Project:", project_data['name'], "###")

        self.process_valid_project(project_data)

    def process_valid_project(self, project_data):
        """Process a valid project by cloning the repo and adding any
        valid files to the databse."""
        try:
            repo, repo_path = self.make_repo(project_data)
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
            except FileNotFoundError:
                pass

    def make_repo(self, project_data):
        """Clone a repository and return a git.Repo object for it."""
        repos_dir = "data/git_projects/temp_repos"
        temp_dir = "temp_{}".format(str(random.randint(0, 2000000)))
        repo_path = os.path.join(repos_dir, temp_dir)

        url = "https://:@github.com/{}/{}.git".format(
            project_data['login'], project_data['name'])

        repo = git.Repo.clone_from(url, repo_path)
        return repo, repo_path

    def add_name_and_gender(self, project_data):
        """Add fullname and gender data to project data."""
        project_data['user_fullname'] = None
        project_data['gender'] = None
        project_data['gender_probability'] = None

        fullname, gender, gender_probability = self.get_fullname_and_gender(
            project_data)

        if gender not in ['nil', None]:
            project_data['user_fullname'] = fullname
            project_data['gender'] = gender
            project_data['gender_probability'] = gender_probability
        elif gender is None:
            self.gender_wait.append(project_data)
        else:
            self.log.info("Gender " + gender + ": " +
                          project_data['login'])

    def get_fullname_and_gender(self, project_data):
        """Collect a github users fullname and gender data if available."""
        fullname = get_fullname(
            project_data['login'], self.session, self.times['session'])

        if fullname not in [None, '']:
            name = fullname.split()[0]
            gender, gender_probability = common.get_gender(
                name, self.database, 'genders')
        else:
            self.log.info("No User Name: " + project_data['login'])

        return fullname, gender, gender_probability

    def add_contributors(self, project_data):
        """Add a list of contributors to project data."""
        project_data['contributors'] = None
        contrib_url = "{}/stats/contributors".format(project_data['url'])
        contribs = self.session.get(contrib_url).json()

        if api_ok(contribs, self.times["session"], write=self.log.info):
            project_data['contributors'] = contribs

    def is_valid_project(self, project_data):
        """Checks to make sure project is valid.

        This means checking for a username and gender, as well as making
        sure that the repository has no more than 1 contributor.
        """
        if project_data['user_fullname'] is None or project_data['gender'] is None:
            return False

        contribs = project_data['contributors']
        if contribs is None or len(contribs) > 1:
            return False

        if (len(contribs) == 1
                and project_data['login'] != contribs[0]['author']['login']):
            return False

        return True

    def process_file(self, path, filename, project_data):
        """Process a file and add it to the database if it is valid."""
        self.totals['files'] += 1
        file_data = self.get_file_data(path, filename)

        if file_data is not None:
            print("Processing File:", "....", filename)

            if self.add_file_to_db(file_data, project_data):
                print("-- Added")
                self.totals['added'] += 1

    def get_file_data(self, path, filename):
        """Gets source code and some file data from a file."""
        try:
            with open(path) as file:
                source = file.read()
        except (FileExistsError, FileNotFoundError,
                UnicodeDecodeError) as error:
            self.log.error("File Error", error)
            return None

        line_count = source.count('\n')
        if self.is_valid_file(path, source, line_count):
            hash_name = hashlib.md5(filename.encode()).hexdigest()
            return [hash_name, filename, source, line_count]

        self.log.info("Lines out of range: " + str(line_count))
        return None

    def is_valid_file(self, path, source, line_count):
        """Checks to see if a file is valid.

        A large part of the validation for files in this class is done
        by github.get_single_author_files. So this is where any final
        validation can be done before adding source code to the database.
        """
        if 10 <= line_count <= 1000:
            return True
        return False

    def add_file_to_db(self, file_data, project_data):
        """Adds a file to the database."""
        values = self.get_entry_values(project_data)
        values.extend(file_data)

        try:
            self.database.insert(self.collection_info.table.columns,
                                 self.collection_info.table.name, values)
        except common.DatabaseError as error:
            self.log.error("In add_file_to_db", error)
            return False

        return True

    def clean_up(self):
        """Prints stats on program run and other final actions."""
        common.Collector.clean_up(self)

        projects = self.totals['projects'] + 0.1
        self.log.info(
            "Projects successfully processed: {:.0f}".format(projects))

        added = self.totals['added']
        files = self.totals['files'] + 0.1
        self.log.info("Files added/checked: {}/{:.0f} {:.0f}%".format(
            added, files, (added / files) * 100))
        self.log.info("Files added/project: {}/{:.0f} {:.0f}%".format(
            added, projects, (added / projects) * 100))

        if self.gender_wait:
            common.write_json_data("{}/{}_{}".format(
                "data/git_projects/missing/", "missing_gender",
                str(time.time())), self.gender_wait)


class GitCollectionInfo(common.CollectionInfo):
    """Information required for collecting source from github."""

    def __init__(self, records, table, validation, limits, git_data):
        super(GitCollectionInfo, self).__init__(
            records, table, validation, limits)
        self.git_data = git_data


class GithubData:
    """Data for a github account."""

    def __init__(self, login, passwd):
        self.login = login
        self.passwd = passwd


class SingleAuthorFilter:
    """Helper class to collect paths for all the single author files
    in a repo."""

    def __init__(self, repo, repo_path, validation, name, login):
        self.repo = repo
        self.repo_path = repo_path
        self.validation = validation
        self.name = name
        self.login = login

    def get_valid_files(self, full_path, relative_path):
        """Gets all the file paths in a repo that are by one author and
        are valid."""
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
        """Checks if a filename is not excluded and has the right extension."""
        if filename in self.validation.exclude_files:
            return False
        return has_extensions(filename, self.validation.extensions)

    def is_excluded_dir(self, dirname):
        """Checks a directory name to se if it is excluded."""
        if dirname in self.validation.exclude_dirs:
            return True
        return False

    def get_blame_count(self, path):
        """Returns a dictionary of contributors on a file and the number
        of contributions they made."""
        count = {}
        try:
            for commit, _ in self.repo.blame(None, path):
                if commit.author in count:
                    count[commit.author.name] += 1
                else:
                    count[commit.author.name] = 1
        except git.exc.GitError:  # pylint: disable=no-member
            pass
        return count

# Functions ############################################################


def authenticated_session(name=None, passwd=None):
    """Create an authenticated requests session for interacting with the
    github api."""
    name = input("Git username: ") if name is None else name
    prompt = "Github Password: "
    return common.requests_session(name, passwd, prompt)


def wait_for_api(session_time, padding, write=print):
    """Sleeps a program until the git api rate limit resets."""
    now = time.time()
    elapsed = now - session_time
    sleep_seconds = 3600 - elapsed + padding

    sleep_time = common.find_time(sleep_seconds)

    write('**** Waiting for github api reset: {} ****'.format(sleep_time))
    write('Elapsed: {}, Current time: {}, Sleeping until: {}'.format(
        common.find_time(elapsed), common.get_time_string(now),
        common.get_time_string(now + sleep_seconds)))

    time.sleep(sleep_seconds)
    write('Slept for: {}'.format(sleep_time))


def api_ok(data, session, padding=120, write=print):
    """Tests the return value from github api for errors."""
    if 'message' in data:
        write("Api issue: {}".format(data['message']))

        if data['message'].find('rate limit exceeded') > -1:
            raise (RateLimitExceeded("Github RateLimit Exceeded"))
        elif data['message'] == 'Server Error':
            time.sleep(10)
        elif data['message'] == 'Bad credentials':
            sys.exit()
        elif data['message'] not in ['Not Found', 'Repository access blocked']:
            write("Git api Error: " + str(data))
            raise GitApiError(str(data))
        return False

    return True


def has_extensions(filename, extensions):
    """Checks to see if a filename ends with one of the given extensions."""
    for ext in extensions:
        if filename.endswith(ext):
            return True
    return False


def get_fullname(login, request_session, session_time):
    """Get a fullname for a github user login."""
    url = "https://api.github.com/users/" + login
    data = request_session.get(url).json()

    try:
        if api_ok(data, session_time) and 'name' in data:
            return data['name']
    except RateLimitExceeded as limit:
        raise limit
    except GitApiError:
        pass

    return None


def get_single_author_files(repo, repo_path, validation, name, login):
    """Returns the filepaths for all single author files from a github
    repository."""
    file_filter = SingleAuthorFilter(repo, repo_path, validation, name, login)
    try:
        return file_filter.get_valid_files(repo_path, "")

    except OSError as error:
        print("OSError (_SingleAuthorFiles):", error)
        return []


# Exceptions ###########################################################


class GitApiError(Exception):
    """Error for fatal GitHub Api errors."""
    pass


class RateLimitExceeded(GitApiError):
    """Error for GitHub Api rate limit reached."""
