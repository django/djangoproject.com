from .common import *  # noqa
from .dev import (  # noqa
    CACHES,
    CSRF_COOKIE_SECURE,
    DEBUG,
    DOCS_BUILD_ROOT,
    EMAIL_BACKEND,
    MEDIA_ROOT,
    PUSH_SSL_CALLBACK,
    SESSION_COOKIE_SECURE,
    SILENCED_SYSTEM_CHECKS,
    STATIC_ROOT,
    THUMBNAIL_DEBUG,
)

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("SQL_DATABASE"),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST"),
        "PORT": os.environ.get("SQL_PORT"),
    }
}

SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = [".localhost", "127.0.0.1", "www.127.0.0.1"]

LOCALE_MIDDLEWARE_EXCLUDED_HOSTS = ["docs.djangoproject.localhost"]

# django-hosts settings
PARENT_HOST = "localhost:8000"

# Enable optional components
if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    INTERNAL_IPS = ["127.0.0.1"]
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.common.CommonMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    MIDDLEWARE.insert(
        MIDDLEWARE.index("debug_toolbar.middleware.DebugToolbarMiddleware") + 1,
        "djangoproject.middleware.CORSMiddleware",
    )
