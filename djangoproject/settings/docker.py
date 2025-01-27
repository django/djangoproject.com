from .common import *  # noqa
from .dev import (  # noqa
    CACHES,
    SILENCED_SYSTEM_CHECKS,
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

DEBUG = True
THUMBNAIL_DEBUG = DEBUG

CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

MEDIA_ROOT = str(DATA_DIR.joinpath("media_root"))

SESSION_COOKIE_SECURE = False

STATIC_ROOT = str(DATA_DIR.joinpath("static_root"))

# Docs settings
DOCS_BUILD_ROOT = DATA_DIR.joinpath("djangodocs")

# django-hosts settings

PARENT_HOST = "localhost:8000"

# django-push settings

PUSH_SSL_CALLBACK = False

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
