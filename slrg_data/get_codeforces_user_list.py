"""Collect the newest codeforces rated user list and save the results in
a proper json file.

Requests a list of all codeforces users that have participated in at
one rated contest. The result of this request is saved to a file
'cf_rated_users.json' in the folder the script is run in

If the request is unsuccessful the response will be printed.

Usage
=====

At the command line run::

    $ slrg-cf-users
"""
# Python imports
import sys
import json

# 3rd Party imports
import requests


# Variables ############################################################

CF_USER_LIST_API = 'https://codeforces.com/api/user.ratedList?'
FILE = 'cf_rated_users.json'


# Functions ############################################################

def _entry():
    main()


def main():
    """Gets a list of rated users from codeforces and writes it to a file."""
    print("Collecting Codeforces Users ...")
    r = requests.get(CF_USER_LIST_API)
    data = r.json()

    if data['status'] != 'OK':
        print("The request failed:", data)
        sys.exit()

    with open(FILE, 'w') as f:
        json.dump(data['result'], f)

    print("User list created:", FILE)
