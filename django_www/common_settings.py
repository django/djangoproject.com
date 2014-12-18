# Settings common to www.djangoproject.com and docs.djangoproject.com
import json
import os

from unipath import FSPath as Path


# Utilities

# The full path to the repository root.
BASE = Path(__file__).absolute().ancestor(2)

# Far too clever trick to know if we're running on the deployment server.
PRODUCTION = ('DJANGOPROJECT_DEBUG' not in os.environ)

# It's a secret to everybody
try:
    with open(BASE.ancestor(1).child('conf').child('secrets.json')) as handle:
        SECRETS = json.load(handle)
except IOError:
    SECRETS = {'secret_key': 'a', 'superfeedr_creds': ['any@email.com', 'some_string']}


# Django settings

ADMINS = ()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': SECRETS.get('memcached_host', '127.0.0.1:11211'),
    } if PRODUCTION else {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trololololol',
    },
}

CACHE_MIDDLEWARE_SECONDS = 60 * 5  # 5 minutes

CSRF_COOKIE_SECURE = PRODUCTION

CSRF_COOKIE_HTTPONLY = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangoproject',
        'USER': 'djangoproject',
        'HOST': SECRETS.get('db_host', ''),
        'PASSWORD': SECRETS.get('db_password', ''),
    },
}

DEBUG = not PRODUCTION

DEFAULT_FROM_EMAIL = "noreply@djangoproject.com"

if not PRODUCTION:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
    }
}
if PRODUCTION:
    LOGGING["handlers"]["syslog"] = {
        "formatter": "full",
        "level": "DEBUG",
        "class": "logging.handlers.SysLogHandler",
        "address": "/dev/log",
        "facility": "local4",
    }
    LOGGING["loggers"]["django.request"]["handlers"].append("syslog")


MANAGERS = ()

MEDIA_ROOT = BASE.ancestor(1).child('media')

MEDIA_URL = '/m/'

SECRET_KEY = str(SECRETS['secret_key'])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

SERVER_EMAIL = "root@djangoproject.com"

SESSION_COOKIE_SECURE = PRODUCTION

SESSION_COOKIE_HTTPONLY = True

STATICFILES_DIRS = [BASE.child('static')]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = BASE.ancestor(1).child('static')

STATIC_URL = '/s/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_DIRS = [BASE.child('templates')]

TIME_ZONE = 'America/Chicago'

USE_I18N = False

USE_L10N = False

USE_TZ = False

SILENCED_SYSTEM_CHECKS = ['1_6.W001']

# django-secure settings

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000  # 1 year

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
