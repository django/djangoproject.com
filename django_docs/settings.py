from django_www.settings import *

PREPEND_WWW = False
TEMPLATE_CONTEXT_PROCESSORS += ["django.core.context_processors.request"]
ROOT_URLCONF = 'django_docs.urls'
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

# Override INSTALLED_APPS so that we only have a few things running on docs.
# Keep around debug_toolbar and raven if the parent settings module installed
# them.
_new_apps = [
    'django.contrib.staticfiles',
    'docs',
    'haystack',
]
if 'debug_toolbar' in INSTALLED_APPS:
    _new_apps.append('debug_toolbar')
if 'raven.contrib.django' in INSTALLED_APPS:
    _new_apps.append('raven.contrib.django')
INSTALLED_APPS = _new_apps

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
]
if PRODUCTION:
    MIDDLEWARE_CLASSES.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE_CLASSES.append('django.middleware.cache.FetchFromCacheMiddleware')

# Where to store the build Sphinx docs.
if PRODUCTION:
    DOCS_BUILD_ROOT = BASE.parent.child('docbuilds')
else:
    DOCS_BUILD_ROOT = '/tmp/djangodocs'

# Haystack settings
HAYSTACK_SITECONF = 'docs.search_sites'
if PRODUCTION:
    HAYSTACK_SEARCH_ENGINE = 'xapian'
    HAYSTACK_XAPIAN_PATH = BASE.parent.child('djangodocs.index')
else:
    HAYSTACK_SEARCH_ENGINE = 'whoosh'
    HAYSTACK_WHOOSH_PATH = '/tmp/djangodocs.index'
