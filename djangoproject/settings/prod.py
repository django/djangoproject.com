from .common import *  # noqa

ALLOWED_HOSTS = [
    'www.djangoproject.com',
    'djangoproject.com',
    'docs.djangoproject.com',
] + SECRETS.get('allowed_hosts', [])

DEBUG = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': SECRETS.get('memcached_host', '127.0.0.1:11211'),
    },
}

CSRF_COOKIE_SECURE = True

HOST_SCHEME = 'https'

LOGGING["handlers"]["syslog"] = {
    "formatter": "full",
    "level": "DEBUG",
    "class": "logging.handlers.SysLogHandler",
    "address": "/dev/log",
    "facility": "local4",
}
LOGGING["loggers"]["django.request"]["handlers"].append("syslog")

MIDDLEWARE_CLASSES = (['django.middleware.cache.UpdateCacheMiddleware'] +
                      MIDDLEWARE_CLASSES +
                      ['django.middleware.cache.FetchFromCacheMiddleware'])

PARENT_HOST = 'djangoproject.com'

SESSION_COOKIE_SECURE = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# django-secure settings

SECURE_HSTS_SECONDS = 31536000  # 1 year

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Docs settings

DOCS_BUILD_ROOT = BASE.parent.child('data').child('docbuilds')

# Haystack settings

HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_XAPIAN_PATH = BASE.parent.child('data').child('djangodocs.index')

PUSH_SSL_CALLBACK = True

# Log errors to Sentry instead of email, if available.
if 'sentry_dsn' in SECRETS and not DEBUG:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {'dsn': SECRETS['sentry_dsn']}
    LOGGING["loggers"]["django.request"]["handlers"].remove("mail_admins")
