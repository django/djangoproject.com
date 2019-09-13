from .common import *  # noqa

ALLOWED_HOSTS = [
    'www.djangoproject.localhost',
    'djangoproject.localhost',
    'docs.djangoproject.localhost',
    'dashboard.djangoproject.localhost',
] + SECRETS.get('allowed_hosts', [])

LOCALE_MIDDLEWARE_EXCLUDED_HOSTS = ['docs.djangoproject.localhost']

DEBUG = True
THUMBNAIL_DEBUG = DEBUG

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trololololol',
    },
    'docs-pages': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'docs-pages',
    },
}

CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = str(DATA_DIR.joinpath('media_root'))

SESSION_COOKIE_SECURE = False

STATIC_ROOT = str(DATA_DIR.joinpath('static_root'))

# Docs settings
DOCS_BUILD_ROOT = DATA_DIR.joinpath('djangodocs')

# django-hosts settings

PARENT_HOST = 'djangoproject.localhost:8000'

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
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        )
        MIDDLEWARE.insert(
            MIDDLEWARE.index('debug_toolbar.middleware.DebugToolbarMiddleware') + 1,
            'djangoproject.middleware.CORSMiddleware'
        )


# Disable for development only.
SILENCED_SYSTEM_CHECKS = SILENCED_SYSTEM_CHECKS + ['captcha.recaptcha_test_key_error']
