Getting Started
===============

On this page there can be technical information on getting setup to use the code and scripts to support data collection. If a person was just going to use our information to inspire their own code they could probably skip this part.

.. Should give all the information on how to install and setup the
.. environment for using the app.
.. use pip3 to install the module.
.. navigate to a folder that you want to store your data and logs etc.
.. run slrg-quickstart
.. when running scripts and code do it from this folder

Installation
------------

Download the slrg_data folder. Could involve downloading or cloning it from the schools gitlab or wherever we store it.

CD into the downloaded folder and run::

    $ pip3 install .

**Note:** You will need to have python3-pip installed.

This will install the slrg_data module so that it can be imported
as a python module as below

    >>> import slrg_data


Setup
-----

Most of the collection functions/scripts assume a specific directory structure. Create a new folder for your data collection to take place in. Cd into it and run::

    $ slgr_quickstart

This will ask some questions about your database and github credentials. (Will probably be able to set some defualts if our current database and github accounts are still active).

    >>> # Should I put an example of the setup script here?

Once complete you will have a directory structure created. Most examples assume that you will be in one of these directories to run code. This will enable scripts to find the configuration and data files, and store log information in the correct places. (link to a configuration section that explains the directory structure and the configuration options).

You are now set up to use the module.

Running The Scripts
-------------------

Some explanation of how to run the scripts can be given here.  There will be more detailed explanation for each script in the section that it is described and in the Api docs.

All scripts will be able to be run in 2 different fashions.

1. At the command line

    ::

        $ script_name

    Any information not stored in the configuration files, such as passwords and filenames, will be asked for before running the script. If you make a mistake entering something you will get an error message and have to start the script again.

2. As a function in the python interpreter

    >>> from slrg_data import script_name
    >>> script_name.main(*args)

    The main difference here is that you can set variables to pass to the functions arguments. This way if you make a mistake or the script exits early you can start it again without having to retype all the information.

    Some of the scripts that process large files will return the entry that they left of with. So you can save it to a variable and call teh function again to start where you left off.

    >>> start = 0
    >>> start = script_name.main(start, *args)
    >>> start = script_name.main(start, *args)
    # .... Until you are done

**Note:** Once again remember that all of these scripts should be run from somewhere inside the directory you have set up.
