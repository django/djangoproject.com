from .common import *  # noqa

ALLOWED_HOSTS = [
    'www.djangoproject.dev',
    'djangoproject.dev',
    'docs.djangoproject.dev',
    'dashboard.djangoproject.dev',
] + SECRETS.get('allowed_hosts', [])

DEBUG = True
THUMBNAIL_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trololololol',
    },
}

CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_SECURE = False

# Docs settings
DOCS_BUILD_ROOT = BASE_DIR.joinpath('djangodocs')

# django-hosts settings

PARENT_HOST = 'djangoproject.dev:8000'

# django-push settings

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
