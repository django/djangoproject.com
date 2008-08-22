from django_website.settings import *

PREPEND_WWW = False
INSTALLED_APPS = []
TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), "templates")] + TEMPLATE_DIRS
ROOT_URLCONF = 'djangodocs.urls'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

if DEVELOPMENT_MODE:
    DOCS_PICKLE_ROOT = "/Users/jacob/Projects/Django/upstream/docs/_build/pickle/"
else:
    DOCS_PICKLE_ROOT = "/home/jacob/django-docs/docs/_build/pickle"
