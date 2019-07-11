Python3 Package
=========================

.. This should be information about the package in general. I think the overall structure of the webpage should not be about the python package, but instead about the project. Then we can have the python package as part of it, not as the whole focus. Or the documentation can be here only to use and support the python project in which case it will not need some of the sections I added.

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


.. _config_lab:

Configuration
-------------

Some of the script information is stored in a configuration file. It can be convinient to save some fields so you don't have to type everything in everytime you run a script.

See scripts(link) for information on passing some arguments as command line options.

.. automodule:: config
   :members:
   :undoc-members:
   :show-inheritance:

