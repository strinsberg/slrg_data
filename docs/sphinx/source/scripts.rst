Scripts
===============

Script information should go here.
There are 2 general issues with running some scripts long term.
* The first is that services can disconnect. The database, the websites,
or the APIs. These can be difficult to recover from because you don't
want to abuse the service when it is unavailable by continuously calling
it.
* The other is large projects for github. Since we are clonign a project
before processing it, there can be size issues. We don't want images
etc. But they will be downloaded. While overall we should not get too
many big projects as we are restricting projects to small numbers of
contributors before cloning, sometimes it happens. The default is just
to chug away and download it, but it might not always be ideal to do
this. I often stop and restart the program if I notice this. 




Git Projects Collection
-----------------------

.. automodule:: slrg_data.collect_git_projects
   :members:
   :undoc-members:
   :show-inheritance:


Git Commits Collection
-----------------------

.. automodule:: slrg_data.collect_git_commits
   :members:
   :undoc-members:
   :show-inheritance:


Codeforces Collection
-----------------------

.. automodule:: slrg_data.collect_codeforces
   :members:
   :undoc-members:
   :show-inheritance:


Gender Codeforces User List
---------------------------

.. automodule:: slrg_data.gender_codeforces
   :members:
   :undoc-members:
   :show-inheritance:


Filter Codeforces User List
---------------------------

.. automodule:: slrg_data.filter_codeforces
   :members:
   :undoc-members:
   :show-inheritance:


Select From Database
--------------------

.. automodule:: slrg_data.select
   :members:
   :undoc-members:
   :show-inheritance:


Combine Json
------------

.. automodule:: slrg_data.combine_json
   :members:
   :undoc-members:
   :show-inheritance:


