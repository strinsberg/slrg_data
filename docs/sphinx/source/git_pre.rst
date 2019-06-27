.. _git_pre:

Pre-processing GitHub Metadata
==============================

Here we can include any instructions that we might want for pre-processing the github data before collecting source code from it.

Currently all I have is information on adding name and gender. Which it may actually turn out is best left for when the script runs in some cases. I still have to decide on how to set that up. But in the future we could maybe have a way to filter the records by country or other attributes. If they had been given gender we could even filter by gender or gender probability (one reason to add it all first)

Adding Name and Gender
-----------------------

You can add name and gender to the github metadata before running the scripts on it. This can be done with the add_git_gender script.

**Example:**

    For git_projects data first navigate to 'your_project/data/git_projects' and open an interpreter.

    >>> from slrg_data import add_git_gender
    >>> filename = "filename.data"  # The file to process
    >>> add_gender_git.main(filename)

    Or from the command line::

        $ add_git_gender

The script will output 2 files. One 'filename_good.data' will contain all the records that were able to have name and gender added. The other 'filename_missing.data' will have all the records for which names were found, but the gender api had reached it's rate limit for the day and the genders database did not have information for the name. (links to information on these)

This script will take a lot of time to run, as it can only process 5k users per hour, due to the github api limits (link to api info). It will print out some information on it's progress and create the output files.

Notes
^^^^^
* This does not have to be done before running the scripts. The git_projects script is slow enough that it rarely uses up the github api limit even if it is collecting name and gender info at the same time. So in some cases it may reduce waiting time if name and gender are collected while running this script.

