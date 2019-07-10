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

Download the slrg_data folder from <wherever we store it>.

CD into the downloaded folder and run::

    $ pip3 install .

**Note:** You will need to have python3-pip installed.

This will install all the scripts to be callable from the command line.

This will also install the slrg_data module so that it can be imported
as a python3 module as below

    >>> import slrg_data

More information on how to use the scripts from the command line or in the python3 interpreter is available in the (link) Scripts section.

Setup
-----

To create a directory for the configuration file and other required folders
Run::

    $ slgr-install

This will create an slrg directory in your home folder. This directories main purpose is to hold a configuration file and to store log files and other temporary files and folders. It is required to run the scripts.

More information can be found in the Configuration (link) section.

Using The module
----------------

Now that the module is setup the scripts can be run. It is recommended that you create a follder to store your data files and any script results.

