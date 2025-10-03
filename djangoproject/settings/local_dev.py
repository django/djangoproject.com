from .dev import *  # noqa

# Override database settings to use SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR.joinpath("djangoproject.sqlite3"),
    },
    "trac": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR.joinpath("trac.sqlite3"),
    },
}

# We don't need the trac database router for SQLite
DATABASE_ROUTERS = []
