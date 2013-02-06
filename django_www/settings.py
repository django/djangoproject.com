# Settings for www.djangoproject.com

import os
import json
import platform
from unipath import FSPath as Path

# The full path to the repository root.
BASE = Path(__file__).absolute().ancestor(2)

# Far too clever trick to know if we're running on the deployment server.
PRODUCTION = ('DJANGOPROJECT_DEBUG' not in os.environ) and ("djangoproject" in platform.node())

# It's a secret to everybody
SECRETS = json.load(open(BASE.parent.child('secrets.json')))
SECRET_KEY = str(SECRETS['secret_key'])
# SUPERFEEDR_CREDS is a 2 element list in the form of [email,secretkey]
SUPERFEEDR_CREDS = SECRETS.get('superfeedr_creds')

ADMINS = (('Adrian Holovaty','holovaty@gmail.com'),('Jacob Kaplan-Moss', 'jacob@jacobian.org'))
MANAGERS = (('Jacob Kaplan-Moss','jacob@jacobian.org'),)
FEED_APPROVERS_GROUP_NAME = "feed-approver"
TIME_ZONE = 'America/Chicago'
SERVER_EMAIL = 'root@djangoproject.com'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangoproject',
        'USER': 'djangoproject'
    },
    'trac': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'code.djangoproject',
        'USER': 'code.djangoproject'
    }
}
DATABASE_ROUTERS = ['tracdb.db_router.TracRouter']

USE_I18N = False
USE_L10N = False

MEDIA_ROOT = BASE.child('media')
MEDIA_URL = '/m/'
TEMPLATE_DIRS = [BASE.child('templates')]
STATICFILES_DIRS = [BASE.child('static')]
STATIC_ROOT = BASE.child('static_root')
STATIC_URL = '/s/'

if PRODUCTION:
    DEBUG = False
    PREPEND_WWW = True
else:
    DEBUG = True
    PREPEND_WWW = False
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1
ROOT_URLCONF = 'django_www.urls'
INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_push.subscriber',
    'blog',
    'accounts',
    'aggregator',
    'cla',
    'docs',
    'svntogit',
    'tracdb',
    'registration',
    'south',
    'djangosecure',
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

CACHE_MIDDLEWARE_SECONDS = 60 * 5 # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'djangoproject'
CACHE_MIDDLEWARE_GZIP = True
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

MIDDLEWARE_CLASSES = [
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]
if PRODUCTION:
    MIDDLEWARE_CLASSES.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE_CLASSES.append('django.middleware.cache.FetchFromCacheMiddleware')

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "docs.context_processors.recent_release",
]


DEFAULT_FROM_EMAIL = "noreply@djangoproject.com"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {"format": "[%(name)s] %(levelname)s: %(message)s"},
        "full": {"format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s"},
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ['require_debug_false'],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django_website": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    }
}
if PRODUCTION:
    LOGGING["handlers"]["logfile"] = {
        "formatter": "full",
        "level": "DEBUG",
        "class": "logging.handlers.TimedRotatingFileHandler",
        "filename": "/var/log/django_website/website.log",
        "when": "D",
        "interval": 7,
        "backupCount": 5,
    }
    LOGGING["loggers"]["django.request"]["handlers"].append("logfile")
    LOGGING["loggers"]["django_website"]["handlers"] = ["logfile"]

# django-registration settings
ACCOUNT_ACTIVATION_DAYS = 3

# comment_utils settings
AKISMET_API_KEY = "c892e4962244"

# setting for documentation root path
DJANGO_DOCUMENT_ROOT_PATH = "/home/html/djangoproject.com/docs/"
DJANGO_TESTS_PATH = "/home/html/djangoproject.com/tests/"

# XXX What's this for?
DJANGO_SVN_ROOT = "http://code.djangoproject.com/svn/django/"

# PubSubHubbub settings
PUSH_HUB = 'https://superfeedr.com/hubbub'
PUSH_CREDENTIALS = 'aggregator.utils.push_credentials'
PUSH_SSL_CALLBACK = PRODUCTION

# Lock down some security stuff
if PRODUCTION:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = False
    # This breaks SVG embedding in docs.
    # TODO: switch to X_FRAME_OPTIONS = 'SAMEORIGIN' in Django 1.4
    # SECURE_FRAME_DENY = True
    SECURE_HSTS_SECONDS = 600
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "SSL")

# If django-debug-toolbar is installed enable it.
if not PRODUCTION:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        # Insert DDT after the common middleware
        common_index = MIDDLEWARE_CLASSES.index('django.middleware.common.CommonMiddleware')
        MIDDLEWARE_CLASSES.insert(common_index+1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
        INSTALLED_APPS.append('debug_toolbar')

# Log errors to Sentry instead of email, if available.
if 'sentry_dsn' in SECRETS:
    INSTALLED_APPS.append('raven.contrib.django')
    SENTRY_DSN = SECRETS['sentry_dsn']
    LOGGING["loggers"]["django.request"]["handlers"].remove("mail_admins")
