"""
Base class for extracting source code for codeforces submissions.
"""
# Standard library modules
from datetime import datetime
import urllib
import time

# 3rd party modules
import requests
from bs4 import BeautifulSoup
import pymysql
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

# My modules
from . import common


class CfSubmissionsCollector(common.Collector):
    """Base class for extracting source code for codeforces submissions."""

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
        """Process user data for a code forces user."""
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
        return 'country' in entry and entry['country'] != '' and entry[
            'country'] is not None

    def get_submissions(self, handle):
        """Get data on the first sub_count submissions for a codeforces user."""
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
        """Processes submissions add valid ones to the database."""
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
        """
        columns = ['problem_name']
        where = ['handle=' + "'" + entry['handle'] + "'"]

        try:
            results = self.database.select(columns,
                                           self.collection_info.table.name,
                                           where)
            names = []
            for tup in results:
                names.append(tup[0])

            return names

        except common.DatabaseError as error:
            self.log.error("In previously collected", error)
            return 0

    def check_limits(self):
        """Checks to see if limits for max submissions have been reached."""
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
        """Processes a submission and adds it to the database."""
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
        """Gets the source code for a submission using direct links."""
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
        """Gets the html for a submissions source code."""
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
        """Checks to see if a submission is valid."""
        if (sub_data['problem']['name'] in problems
                or sub_data["verdict"] != "OK"
                or sub_data["problem"]["type"] != "PROGRAMMING"
                or len(sub_data["author"]["members"]) > 1
                or "teamName" in sub_data['author']):
            return False

        if not self.valid_language(sub_data):
            return False

        return self.valid_language(sub_data)

    def valid_language(self, sub_data):
        """Check to see if a submission's programming language is valid."""
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
        """Adds a submission to desired table in the data base."""
        values = self.get_sub_values(sub_data, source)
        values.extend(self.get_entry_values(entry))

        try:
            self.database.insert(self.collection_info.table.columns,
                                 self.collection_info.table.name, values)
        except common.DatabaseError as error:
            self.log.error("In add_sub_to_db", error)
            return False

        return True

    def get_sub_values(self, sub_data, source):
        """Gets the submission values needed to add it to the database."""
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
        """if a value needs to be transformed it is done in here.

        For example timestamps are transformed into readable strings.
        """
        v = value
        if v is not None and entry_field == "registrationTimeSeconds":
            v = common.get_time_string(v)
        return v

    def clean_up(self):
        """See Collector"""
        common.Collector.clean_up(self)

        added = self.totals['added']
        subs = self.totals['subs'] + 0.1
        self.log.info("Users successfully processed: {}".format(
            self.totals['users']))
        self.log.info("Submissions added/checked {}/{:.0f} {:.0f}%".format(
            added, subs, (added / subs) * 100))


class CfSeleniumCollector(CfSubmissionsCollector):
    """Extracts source code from code forces using the selenium web driver."""

    def __init__(self, database, collection_info, log):
        CfSubmissionsCollector.__init__(self, database, collection_info, log)
        self.driver = None

    def set_up(self):
        """Sets up the webdriver."""
        CfSubmissionsCollector.set_up(self)
        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(5)

    def process_submissions(self, submissions, entry):
        """Extends Extract process submissions with selenium."""
        url = "https://codeforces.com/submissions/" + entry['handle']
        try:
            while True:
                self.driver.get(url)
                break
        except selenium.common.exceptions.TimeoutException:
            print("Timeout: refreshing")
        CfSubmissionsCollector.process_submissions(self, submissions, entry)

    def get_source(self, sub_data):
        """Gets a submissions source using selenium."""
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
        elem = self.driver.find_element_by_link_text(sub_id)
        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
        elem.send_keys(Keys.RETURN)

    def close_popup(self):
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
                except selenium.common.exceptions.TimeoutException:
                    print("Timeout: Trying to refresh again")

    def get_lang(self, sub_data):
        """Returns the file extension for the submissions programming
        language.
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
        """Extends cleanup to close the web driver."""
        CfSubmissionsCollector.clean_up(self)
        if self.driver is not None:
            self.driver.close()


def add_gender(user_data, database, gender_table):
    gender, prob = None, None
    if 'firstName' in user_data:
        gender, prob = common.get_gender(
            user_data['firstName'].split()[0], database, gender_table)
    user_data['gender'] = gender
    user_data['gender_probability'] = prob


class CfCollectionInfo(common.CollectionInfo):
    def __init__(self, records, table, limits, languages):
        super(CfCollectionInfo, self).__init__(
            records, table, None, limits)
        self.languages = languages


class CfLimitData(common.LimitData):
    def __init__(self, start, count, sub_start, sub_count, max_subs,
                 max_no_source):
        super(CfLimitData, self).__init__(start, count)
        self.sub_start = sub_start
        self.sub_count = sub_count
        self.max_subs = max_subs
        self.max_no_source = max_no_source
