from .common import *  # noqa

ALLOWED_HOSTS = [
    'www.djangoproject.dev',
    'djangoproject.dev',
    'docs.djangoproject.dev',
] + SECRETS.get('allowed_hosts', [])

DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trololololol',
    },
}

CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PARENT_HOST = 'djangoproject.dev:8000'

SESSION_COOKIE_SECURE = False

# Docs settings
DOCS_BUILD_ROOT = BASE.child('djangodocs')

# Haystack settings
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = BASE.child('djangodocs.index')

PUSH_SSL_CALLBACK = False

# Enable optional components

if DEBUG:
    try:
        import debug_toolbar  # NOQA
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
