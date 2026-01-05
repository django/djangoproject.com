update_metrics local setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

When running::

    python manage.py update_metrics

locally, you may see::

    permission denied for table ticket

This is a local setup requirement, not a production issue.

Required steps:

1. Create the databases::

       createdb djangoproject
       createdb code.djangoproject

2. Import the Trac schema::

       psql -d code.djangoproject < tracdb/trac.sql

3. Ensure the PostgreSQL user configured in
   ``settings/common.py`` has permission to read tables
   in ``code.djangoproject``.

After this setup, ``update_metrics`` should run successfully.
