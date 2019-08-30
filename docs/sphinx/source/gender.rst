.. _gender_collection:

Gender Collection
=================

Gender collection is done with the |genderize| API. There is more information
in the |gender-report| of the technical report.

Rate Limit
----------

The most important thing to note is that the genderize.io API has a rate limit.
For free users there is a limit of 1000 requests in a 24 hour period. Once this limit is exceeded the API will not return proper results.

The scripts are all setup to store results in the genders table of the database.
This table is checked before any API calls are made to reduce the number of
requests. If the name is not in the database then the API is called. If the
rate limit has been reached no call will be made.

It is safe to run the scripts even after the API limit has been reached for the
day, but it will only classify names that are already stored in the database.


.. links

.. |genderize| raw:: html

   <a href="https://genderize.io" target="_blank">genderize.io</a>

.. |gender-report| raw:: html

    <a href="./_static/technical_report.pdf#page=30" target="_blank">Gender section</a>