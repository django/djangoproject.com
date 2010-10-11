from fabric.api import *

env.hosts = ['ve.djangoproject.com']

def copy_db():
    """
    Copy the production DB locally for testing.
    """
    local('ssh %s pg_dump -U djangoproject -c djangoproject | psql djangoproject' % env.hosts[0])