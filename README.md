slrg_data python3 package
=========================

Work done as a summer reasearch assistant at the University of Lethbridge for Dr. Jackie Rice.

**Disclaimer** this code was not intended for use outside of the reasearch lab. If you choose to use any part of it you do so at your own risk and I will not take responsibility for any results or provide any help/maintenance.

Scripts to collect source code data from github and codeforces.

There is more detailed instructions and information in the docs folder. A pdf of a technical report is in `slrg_data/docs/report`. A detailed walkthrough of how to use this package is available in html format in the html folder. To access run `$ make docs` and open the file `slrg_data/docs/html/index.html`.

Installation
------------

From this folder run

```
$ pip3 install --user .
```

or if you don't want to use pip3

```
$ python3 setup.py install --user
```

This will install several scripts for you to access from the command line. And a .slrg folder with a configuration file and more in `~/.local` on linux and `%APPDATA%` on windows.

**NOTE**: All development was done on Linux and I cannot guarantee that it will work exactly the same on Windows.

More detailed info for each script and how to run them is available in the html documentation.

