# Settings for docs.djangoproject.com

from django_www.common_settings import *


### Django settings

ALLOWED_HOSTS = ['docs.djangoproject.com']

CACHE_MIDDLEWARE_KEY_PREFIX = 'djangodocs'

INSTALLED_APPS = [
    'django.contrib.redirects',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'djangosecure',
    'haystack',
    'south',

    'docs',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'docs.context_processors.docs_version',
    'django.core.context_processors.request',
]

ROOT_URLCONF = 'django_docs.urls'

SITE_ID = 2

USE_I18N = True
LANGUAGE_CODE = 'en'

### Docs settings

if PRODUCTION:
    DOCS_BUILD_ROOT = BASE.parent.child('data').child('docbuilds')
else:
    DOCS_BUILD_ROOT = BASE.child('djangodocs')


### Haystack settings

HAYSTACK_SITECONF = 'docs.search_sites'

if PRODUCTION:
    HAYSTACK_SEARCH_ENGINE = 'xapian'
    HAYSTACK_XAPIAN_PATH = BASE.parent.child('data').child('djangodocs.index')
else:
    HAYSTACK_SEARCH_ENGINE = 'whoosh'
    HAYSTACK_WHOOSH_PATH = BASE.child('djangodocs.index')


### South settings

SOUTH_TESTS_MIGRATE = False


### Enable optional components

if DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        INSTALLED_APPS.append('debug_toolbar')
        INTERNAL_IPS = ['127.0.0.1']
        MIDDLEWARE_CLASSES.insert(
            MIDDLEWARE_CLASSES.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware')

# Log errors to Sentry instead of email, if available.
if 'sentry_dsn' in SECRETS and not DEBUG:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {'dsn': SECRETS['sentry_dsn']}
    LOGGING["loggers"]["django.request"]["handlers"].remove("mail_admins")
