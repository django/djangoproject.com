from .common import *  # noqa

ALLOWED_HOSTS = [
    "www.djangoproject.com",
    "djangoproject.com",
    "docs.djangoproject.com",
    "dashboard.djangoproject.com",
] + SECRETS.get("allowed_hosts", [])

LOCALE_MIDDLEWARE_EXCLUDED_HOSTS = ["docs.djangoproject.com"]

DEBUG = False
THUMBNAIL_DEBUG = DEBUG

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": SECRETS.get("cache_default_url", "redis://localhost:6379"),
    },
    # We use a separate cache for docs so we can purge it when docs are rebuilt
    "docs-pages": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": SECRETS.get("cache_docs_url", "redis://localhost:6379/2"),
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

MEDIA_ROOT = str(DATA_DIR.joinpath("media"))

MEDIA_URL = "https://media.djangoproject.com/"

MIDDLEWARE = (
    ["django.middleware.cache.UpdateCacheMiddleware"]
    + MIDDLEWARE
    + ["django.middleware.cache.FetchFromCacheMiddleware"]
)

SESSION_COOKIE_SECURE = True

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

STATIC_ROOT = str(DATA_DIR.joinpath("static"))

STATIC_URL = "https://static.djangoproject.com/"

# Docs settings
DOCS_BUILD_ROOT = DATA_DIR.joinpath("data", "docbuilds")

# django-hosts settings

HOST_SCHEME = "https"

PARENT_HOST = "djangoproject.com"

# django-push settings

PUSH_SSL_CALLBACK = True

# Log errors to Sentry instead of email, if available.
if "sentry_dsn" in SECRETS and not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SECRETS["sentry_dsn"],
        integrations=[
            DjangoIntegration(transaction_style="function_name"),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=1.0,
    )

# RECAPTCHA KEYS
# Defaults will trigger 'django_recaptcha.recaptcha_test_key_error' system check
if "recaptcha_public_key" in SECRETS:
    RECAPTCHA_PUBLIC_KEY = SECRETS.get("recaptcha_public_key")
    RECAPTCHA_PRIVATE_KEY = SECRETS.get("recaptcha_private_key")

RECAPTCHA_REQUIRED_SCORE = 0.9
