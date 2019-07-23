"""Classes and functions for collecting source code samples from
Codeforces.
"""
from datetime import datetime
import urllib
import time

# 3rd party libraries
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException

# My modules
from . import common


# Collectors ###########################################################

class CfSubmissionsCollector(common.Collector):
    """Concrete class for collecting submission source code from
    Codeforces with direct links.

    Adds 'users', 'subs', 'added', 'user_nosrc', and 'user_subs' keys
    to the totals dict attribute inherited from
    :class:`~slrg_data.collection.common.Collector`.

    See :ref:`Codeforces Collection <cf-collection>` for more information
    on the process.
    """

    def __init__(self, database, collection_info, log):
        common.Collector.__init__(self, database, collection_info, log)
        self.totals.update({
            'users': 0,
            'subs': 0,
            'added': 0,
            'user_nosrc': 0,
            'user_subs': 0
        })

    def process(self, entry):
        """Processes an entry for a single codeforces user.

        Args:
            entry (dict): A row of user data from the Codeforces API
                with any additional user information needed.
        """
        handle = entry['handle']
        print("##", self.totals["entry"], "##", "User:", handle, "####")

        if not self.has_country(entry):
            self.log.info("No Country: " + handle)
            return

        submissions = self.get_submissions(handle)

        if submissions is not None:
            print("-- Received Submissions")
            self.totals['users'] += 1
            self.process_submissions(submissions, entry)
        else:
            print("-- No Submissions")

    def has_country(self, entry):
        """Returns true if a user has a country."""
        return 'country' in entry and entry['country'] != '' and entry[
            'country'] is not None

    def get_submissions(self, handle):
        """Gets submission data for a Codeforces user.

        The number of submissions that are collected depends on the
        limits set collection_info.

        Args:
            handle (str): A codeforces user handle.

        Returns:
            list: A list of json records for the submissions requested
                from the Codeforces API. If there is an issue getting
                the submissions None is returned.
        """
        options = {
            "handle": handle,
            "from": self.collection_info.limits.sub_start,
            "count": self.collection_info.limits.sub_count
        }
        req = requests.get("http://codeforces.com/api/user.status",
                           params=options)
        data = req.json()

        if data["status"] == "OK":
            return data["result"]

        print('API status:', data['status'], 'Comment:', data['comment'])
        return None

    def process_submissions(self, submissions, entry):
        """Collects source code for valid submissions and adds them to
        the database.

        Args:
            submissions (list): A list of submissions for a user.
            entry (dict): A row of user data from the Codeforces API
                with any additional user information needed.
        """
        collected_problems = self.previously_collected(entry)
        self.totals['user_subs'] = len(collected_problems)
        print('-- Already had subs:', self.totals['user_subs'])

        problems = set(collected_problems)

        for sub_data in submissions:
            if not self.check_limits():
                break

            self.totals['subs'] += 1
            if self.is_valid(sub_data, problems):
                print("Processing submission:",
                      sub_data['id'], sub_data['problem']['name'])
                self.process_sub(sub_data, entry, problems)

    def previously_collected(self, entry):
        """Returns a list of previously collected problem names for the user.

        Args:
            entry (dict): A row of user data from the Codeforces API
                with any additional user information needed.

        Returns:
            list: A list of problem names that are already in the
                database for the Codeforces user.
        """
        columns = ['problem_name']
        where = ['handle=' + "'" + entry['handle'] + "'"]

        try:
            results = self.database.select(
                columns, self.collection_info.table.name, where)
            names = []
            for tup in results:
                names.append(tup[0])

            return names

        except common.DatabaseError as error:
            self.log.error("In previously collected", error)
            return 0

    def check_limits(self):
        """Checks to see if given codeforces limits have been reached.

        Checks the total number of submissions and the total number of
        submissions that no source was found for.

        Returns:
            bool: False if one of the limits has been reached,
                otherwise True.
        """
        if self.totals['user_subs'] >= self.collection_info.limits.max_subs:
            self.log.info("-- Reached {} valid submissions added".format(
                self.collection_info.limits.max_subs))
            return False

        if self.totals['user_nosrc'] >= self.collection_info.limits.max_no_source:
            self.log.info("-- Reached {} submissions with no source".format(
                self.collection_info.limits.max_subs))
            return False

        return True

    def process_sub(self, sub_data, entry, problems):
        """Collects the source for a valid submission and adds it along with relevant submission info to the database.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.
            entry (dict): A row of user data from the Codeforces API
                with any additional user information needed.
            problems (set): A set of problems to be updated if the
                submission is successfully added to the database.
        """
        source = self.get_source(sub_data)
        if source is None:
            self.totals['user_nosrc'] += 1
            print("-- No Source({})".format(self.totals['user_nosrc']))
            return

        if self.add_sub_to_db(sub_data, source, entry):
            self.totals['added'] += 1
            self.totals['user_subs'] += 1
            print("--", self.totals['user_subs'], "-- Added:",
                  sub_data['problem']['name'])
            problems.add(sub_data['problem']['name'])

    def get_source(self, sub_data):
        """Collects the source code for a submission using direct links.

        Attempts to create a url from submission data that will lead to
        a page containing the source code for the submission. Even when
        valid links can be constructed the pages are not always
        available so this function often returns None.

        See :ref:`Codeforces Collection <cf-collection>` for more
        information.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.

        Returns:
            str: The source code for a submission if it can be obtained,
                otherwise None.
        """
        if "contestId" not in sub_data:
            return None

        contest_id = sub_data["contestId"]
        sub_id = sub_data["id"]

        html = self.get_source_html(contest_id, sub_id)
        if html is not None:
            soup = BeautifulSoup(html, "html.parser")
            source = soup.find(id="program-source-text")

            if source is not None:
                return source.get_text()

        return None

    def get_source_html(self, contest_id, sub_id):
        """Gets the html for a submissions source code.

        Uses a direct link to scrape the page containing the submissions
        source code.

        Args:
            contest_id (str): The id of the contest the submission was
                submitted during.
            sub_id (str): The id of the submission

        Returns:
            str: The html for a page containing the source code.
        """
        try:
            url = "http://codeforces.com/contest/{}/submission/{}".format(
                contest_id, sub_id)
            with urllib.request.urlopen(url) as request:
                req = request.read()
            return req.decode()

        except urllib.error.URLError as error:
            self.log.error("Getting source Html", error)
            return None

    def is_valid(self, sub_data, problems):
        """Checks to see if a submission is valid.

        See :ref:`Codeforces Collection <cf-collection>` for more
        information on what makes a submission valid.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.
            problems (set): The problems already stored in the database.

        Returns:
            bool: True if the submission is valid, otherwise False.
        """
        if (sub_data['problem']['name'] in problems
                or sub_data["verdict"] != "OK"
                or sub_data["problem"]["type"] != "PROGRAMMING"
                or len(sub_data["author"]["members"]) > 1
                or "teamName" in sub_data['author']):
            return False

        return self.valid_language(sub_data)

    def valid_language(self, sub_data):
        """Check to see if a submission has a language being collected.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.

        Returns:
            bool: True if the language of the submission is one
                being collected, otherwise False.
        """
        language = sub_data["programmingLanguage"]
        new_lang = None
        for lang in self.collection_info.validation.collect:
            if language.find(lang) > -1:
                new_lang = lang

        if new_lang is not None:
            for lang in self.collection_info.validation.exclude:
                if language.find(lang) > -1:
                    self.log.info("Matched bad language: " + language)
                    return False

            sub_data["programmingLanguage"] = new_lang
            return True

        return False

    def add_sub_to_db(self, sub_data, source, entry):
        """Attempts to add all necessary information for a source code
        sample to the database.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.
            source (str): The source code for the submission.
            entry (dict): A row of user data from the Codeforces API
                with any additional user information needed.

        Returns:
            bool: True if the information was successfully added to
                the database, otherwise False.
        """
        values = self.get_sub_values(sub_data, source)
        values.extend(self.get_entry_values(entry))

        if self.database.insert(self.collection_info.table.columns,
                                self.collection_info.table.name, values):
            return True
        return False

    def get_sub_values(self, sub_data, source):
        """Gets the submission values needed to add it to the database.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.
            source (str): The source code for the submission.

        Returns:
            list: A list of all the submission values in the same order
                as their corresponding column in
                collection_info.table.columns.
        """
        difficulty = None
        if 'rating' in sub_data['problem']:
            difficulty = sub_data['problem']['rating']

        creation = sub_data['creationTimeSeconds']
        str_time = common.get_time_string(creation)
        date = datetime.utcfromtimestamp(int(creation))

        return [
            sub_data['id'], source, sub_data['programmingLanguage'],
            sub_data['problem']['name'], difficulty,
            sub_data['author']['participantType'], str_time, date.year,
            date.month, date.day
        ]

    def tranform_entry_value(self, value, entry_field):
        """Transforms any entry values that need it.

        Currently only transforms the registration timestamp into a
        readable string.

        Args:
            value: The value to possible transform.
            entry_field: The field in the entry json. This is used to
                determine if the value needs to be transformed.

        Returns:
            The transformed value if it needed to be transformed or the
                original value if it did not.
        """
        v = value
        if v is not None and entry_field == "registrationTimeSeconds":
            v = common.get_time_string(v)
        return v

    def clean_up(self):
        """Prints details of the collection for users and submissions
        processed.

        Extends :func:`Collector.clean_up() <slrg_data.collection.common.Collector.clean_up>`.
        """
        common.Collector.clean_up(self)

        added = self.totals['added']
        subs = self.totals['subs'] + 0.1
        self.log.info("Users successfully processed: {}".format(
            self.totals['users']))
        self.log.info("Submissions added/checked {}/{:.0f} {:.0f}%".format(
            added, subs, (added / subs) * 100))


class CfSeleniumCollector(CfSubmissionsCollector):
    """Extends CfSubmissionCollector to collect Codeforces source code
    samples using the selenium webdriver.

    This process first tries to collect source with selenium, but it for
    some reason it can't it will fall back on the direct link method
    used by it's parent class. Because direct links are used less often
    this way they are usually available and help to ensure that as many
    samples as possible can be collected.

    The webdrive is setup to use firefox. The firefox browser will be
    needed to use this class (or you will have to change it).

    When running an browser will be opened on the desktop and automatically
    navigate to the pages it needs to collect data. Interacting
    with it or you may interupt and crash the collection. However, if
    for some reason you want to end the program you can close the
    browser window.

    See :ref:`Codeforces Collection <cf-collection>` for more information
    on this process.

    Attributes:
        driver: The selenium webdriver object.
    """

    def __init__(self, database, collection_info, log):
        CfSubmissionsCollector.__init__(self, database, collection_info, log)
        self.driver = None

    def set_up(self):
        """Extends :func:`Collector.set_up() <slrg_data.collection.common.Collector.set_up>`
        to setup the webdriver.
        """
        CfSubmissionsCollector.set_up(self)
        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(5)

    def process_submissions(self, submissions, entry):
        """Extends the extraction process to attempt collecting source
        code using selenium.

        Args:
            submissions (list): A list of submissions for a user.
            entry (dict): A row of user data from the Codeforces API
                with any additional user information needed.
        """
        url = "https://codeforces.com/submissions/" + entry['handle']
        try:
            while True:
                self.driver.get(url)
                break
        except TimeoutException:
            print("Timeout: refreshing")
        CfSubmissionsCollector.process_submissions(self, submissions, entry)

    def get_source(self, sub_data):
        """Gets the source code for a submission if possible.

        Opens the source popup if possible.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.

        Returns:
            str: The source code for a submission if it can be obtained,
                otherwise None.
        """
        try:
            self.open_popup(str(sub_data['id']))
            source = self.get_source_text(sub_data)
            self.close_popup()

            if source is None:
                time.sleep(30)
            return source

        except (ValueError, NoSuchElementException):
            print("Sub not clickable")

        return None

    def get_source_text(self, sub_data):
        """Collects the source code text from an open source popup or
        with a direct link.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.

        Returns:
            str: The source code for a submission if it can be obtained,
                otherwise None.
        """
        time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tag = 'source-popup-source prettyprint linenums lang-' + \
            self.get_lang(sub_data) + " prettyprinted"
        code = soup.find('code', {'class': tag})

        src_html = []
        for tag in code.find_all('li'):
            src_html.append(tag.text)

        if src_html:
            source = "\n".join(src_html)
        else:
            source = super(CfSeleniumCollector, self).get_source(sub_data)
        return source

    def open_popup(self, sub_id):
        """Open a submissions source code popup with selenium.

        Args:
            sub_id (str): The id of the submission.
        """
        elem = self.driver.find_element_by_link_text(sub_id)
        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
        elem.send_keys(Keys.RETURN)

    def close_popup(self):
        """closes an open source code popup if possible.

        If the popup cannot be properly closed for some reason the
        submissions page is refreshed instead. If the page takes to long
        to refresh it will attempt to refresh it again until it loads
        properly.
        """
        try:
            close = self.driver.find_element_by_class_name('close')
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", close)
            close.send_keys(Keys.RETURN)
            time.sleep(2)
        except ElementNotInteractableException as error:
            print(error)
            while True:
                try:
                    self.driver.refresh()
                    break
                except TimeoutException:
                    print("Timeout: Trying to refresh again")

    def get_lang(self, sub_data):
        """Returns a file extension for the language that the submission
        was written in.

        This is needed for finding the source code in the html of the
        once the popup is opened.

        If languages other than C++, Python, and Java are being collected
        their extensions will need to be added to this function or
        it will need to be overridden in a subclass.

        Args:
            sub_data (dict): The submissions information that was
                obtained from the Codeforces API.

        Returns:
            str: The extension if the language is C++, Python, or Java.
                Otherwise the empty string is returned.
        """
        language = sub_data['programmingLanguage']
        if language.find("C++") > -1:
            return 'cpp'
        if language.find('Python') > -1:
            return 'py'
        if language.find('Java') > -1:
            return 'java'
        return ''

    def clean_up(self):
        """Closes the web driver.

        Extends :func:`Collector.clean_up() <slrg_data.collection.common.Collector.clean_up>`.
        """
        CfSubmissionsCollector.clean_up(self)
        if self.driver is not None:
            self.driver.close()


# Collection Info ######################################################

class CfCollectionInfo(common.CollectionInfo):
    """Collection info for Codeforces collection.

    Attributes:
        languages (LanguageData): Programming languages to include or
            exclude from collection.
    """

    def __init__(self, records, table, limits, languages):
        super(CfCollectionInfo, self).__init__(
            records, table, None, limits)
        self.languages = languages


class CfLimitData(common.LimitData):
    """Extended limit data for Codeforces collection.

    Attributes:
        sub_start (int): The submission to start with when getting
            submissions with the Codeforces API.
        sub_count (int): The total number of submissions to request
            from the Codeforces API.
        max_subs (int): The maximum number of source code samples to
            collect for a single Codeforces user.
        max_no_source (int): The number of submissions that no source
            is available for to process before moving on to the next
            user.
    """

    def __init__(self, start, count, sub_start, sub_count, max_subs,
                 max_no_source):
        super(CfLimitData, self).__init__(start, count)
        self.sub_start = sub_start
        self.sub_count = sub_count
        self.max_subs = max_subs
        self.max_no_source = max_no_source


# Functions ############################################################

def add_gender(user_data, database, gender_table):
    """Adds gender data to a Codeforces user record.

    Will attempt to use the gender API if the gender information is
    not in the database.

    Args:
        user_data (dict): A row of user data from the Codeforces API
                with any additional user information needed.  
        database (Database): The local database where gender information
            is stored.
        gender_table (str): The name of the table in the database where
            the gender information is stored. 
    """
    gender, prob = None, None
    if 'firstName' in user_data:
        gender, prob = common.get_gender(
            user_data['firstName'].split()[0], database, gender_table)
    user_data['gender'] = gender
    user_data['gender_probability'] = prob
