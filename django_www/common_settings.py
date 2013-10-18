# Settings common to www.djangoproject.com and docs.djangoproject.com

import json
import os
import platform

from unipath import FSPath as Path


### Utilities

# The full path to the repository root.
BASE = Path(__file__).absolute().ancestor(2)

# Far too clever trick to know if we're running on the deployment server.
PRODUCTION = ('DJANGOPROJECT_DEBUG' not in os.environ)

# It's a secret to everybody
with open(BASE.parent.child('secrets.json')) as handle:
    SECRETS = json.load(handle)


### Django settings

ADMINS = (
    ('Adrian Holovaty', 'holovaty@gmail.com'),
    ('Jacob Kaplan-Moss', 'jacob@jacobian.org'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    } if PRODUCTION else {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    },
}

CACHE_MIDDLEWARE_SECONDS = 60 * 5 # 5 minutes

CSRF_COOKIE_SECURE = PRODUCTION

CSRF_COOKIE_HTTPONLY = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangoproject',
        'USER': 'djangoproject'
        'HOST': SECRETS.get('db_host', 'localhost'),
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


MANAGERS = (
    ('Jacob Kaplan-Moss', 'jacob@jacobian.org'),
)

MEDIA_ROOT = BASE.child('media')

MEDIA_URL = '/m/'

SECRET_KEY = str(SECRETS['secret_key'])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

SERVER_EMAIL = "root@djangoproject.com"

SESSION_COOKIE_SECURE = PRODUCTION

SESSION_COOKIE_HTTPONLY = True

STATICFILES_DIRS = [BASE.child('static')]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

STATIC_ROOT = BASE.child('static_root')

STATIC_URL = '/s/'

TEMPLATE_DIRS = [BASE.child('templates')]

TIME_ZONE = 'America/Chicago'

USE_I18N = False

USE_L10N = False

USE_TZ = False


### django-secure settings

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 600
