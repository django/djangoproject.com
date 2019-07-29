from .common import *  # noqa

ALLOWED_HOSTS = [
    'www.djangoproject.com',
    'djangoproject.com',
    'docs.djangoproject.com',
    'dashboard.djangoproject.com',
] + SECRETS.get('allowed_hosts', [])

LOCALE_MIDDLEWARE_EXCLUDED_HOSTS = ['docs.djangoproject.com']

DEBUG = False
THUMBNAIL_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': SECRETS.get('memcached_host', '127.0.0.1:11211'),
        'BINARY': True,
        'OPTIONS': {
            'tcp_nodelay': True,
            'ketama': True
        }
    },
    'docs-pages': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': SECRETS.get('redis_host', 'localhost:6379'),
        'OPTIONS': {
            'DB': 2,
        },
    },
}

CSRF_COOKIE_SECURE = True

LOGGING["handlers"]["syslog"] = {
    "formatter": "full",
    "level": "DEBUG",
    "class": "logging.handlers.SysLogHandler",
    "address": "/dev/log",
    "facility": "local4",
}
LOGGING["loggers"]["django.request"]["handlers"].append("syslog")

MEDIA_ROOT = str(DATA_DIR.joinpath('media'))

MEDIA_URL = 'https://media.djangoproject.com/'

MIDDLEWARE = (
    ['django.middleware.cache.UpdateCacheMiddleware'] +
    MIDDLEWARE +
    ['django.middleware.cache.FetchFromCacheMiddleware']
)

SESSION_COOKIE_SECURE = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = str(DATA_DIR.joinpath('static'))

STATIC_URL = 'https://static.djangoproject.com/'

# Docs settings
DOCS_BUILD_ROOT = DATA_DIR.joinpath('data', 'docbuilds')

# django-hosts settings

HOST_SCHEME = 'https'

PARENT_HOST = 'djangoproject.com'

# django-push settings

PUSH_SSL_CALLBACK = True

# Log errors to Sentry instead of email, if available.
if 'sentry_dsn' in SECRETS and not DEBUG:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {'dsn': SECRETS['sentry_dsn']}

# RECAPTCHA KEYS
# Defaults will trigger 'captcha.recaptcha_test_key_error' system check
if 'recaptcha_public_key' in SECRETS:
    RECAPTCHA_PUBLIC_KEY = SECRETS.get('recaptcha_public_key')
    RECAPTCHA_PRIVATE_KEY = SECRETS.get('recaptcha_private_key')
