Getting Started
===============

All of the scripts are contained within the python3 package *slrg_data*. This package is available to download <Where?>. Once you have downloaded it follow the instructions below to install the package and setup the configuration file.

The package must be installed to run the scripts. After installation continue to the :ref:`GitHub <git-collection>` or :ref:`Codeforces <cf-collection>` sections for more information on collecting code samples from those sources.

.. _installation:

Installation
------------

CD into the downloaded slrg_data folder and run::

    $ pip3 install --user .

.. note:: If pip3 is not installed on your system see https://pip.pypa.io/en/stable/installing/ for more information.

The installation will install all the command line scripts. It will also create a directory with a configuration file and some other directories necessary for running the scripts.

* Linux: :code:`$ ~/.local/slrg`
* Windows: :code:`%APPDATA%\Python\slrg`

The install will also make the slrg_data package and its contents importable. 

    >>> import slrg_data
    >>> import slrg_data.collect_git_projects
    >>> from slrg_data import collect_git_projects

The :ref:`Scripts section <scripts>` has more information on using scripts from the command line or with imports.

.. _config_lab:

Configuration
-------------

.. automodule:: config
   :members:
   :undoc-members:
   :show-inheritance:
