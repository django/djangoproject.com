from django_website.settings.www import *

PREPEND_WWW = False
APPEND_SLASH = True
INSTALLED_APPS = [
	'django_website.docs',
	'haystack',
]
TEMPLATE_CONTEXT_PROCESSORS += ["django.core.context_processors.request"]
ROOT_URLCONF = 'django_website.urls.docs'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

# Where to store the build Sphinx docs.
if PRODUCTION:
    DOCS_BUILD_ROOT = BASE.ancestor(2).child('docbuilds')
else:
    DOCS_BUILD_ROOT = '/tmp/djangodocs'

# Haystack settings
HAYSTACK_SITECONF = 'django_website.docs.search_sites'
if PRODUCTION:
	HAYSTACK_SEARCH_ENGINE = 'solr'
	HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
else:
	HAYSTACK_SEARCH_ENGINE = 'whoosh'
	HAYSTACK_WHOOSH_PATH = '/tmp/djangodocs.index'
