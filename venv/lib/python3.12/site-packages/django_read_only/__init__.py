from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Callable

from django.apps import AppConfig
from django.conf import settings
from django.core.signals import setting_changed
from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.signals import connection_created

try:
    from psycopg.sql import Composable

    HAVE_PSYCOPG = True
except ImportError:  # pragma: no cover
    HAVE_PSYCOPG = False

read_only = False
ipython_extension_loaded = False


class DjangoReadOnlyAppConfig(AppConfig):
    name = "django_read_only"
    verbose_name = "django-read-only"

    def ready(self) -> None:
        set_read_only()

        for alias in connections:
            connection = connections[alias]
            install_hook(connection)
        connection_created.connect(install_hook)

        setting_changed.connect(reset_read_only)


def set_read_only() -> None:
    global read_only
    if settings.is_overridden("DJANGO_READ_ONLY"):
        read_only = settings.DJANGO_READ_ONLY
    else:
        read_only = bool(os.environ.get("DJANGO_READ_ONLY", ""))


def reset_read_only(setting: str, **kwargs: object) -> None:
    if setting == "DJANGO_READ_ONLY":
        set_read_only()


def install_hook(connection: BaseDatabaseWrapper, **kwargs: object) -> None:
    """
    Rather than use the documented API of the `execute_wrapper()` context
    manager, directly insert the hook. This is done because:
    1. Deleting the context manager closes it, so it's not possible to enter it
       here and not exit it, unless we store it forever in some variable.
    2. We want to be idempotent and only install the hook once.
    """
    if blocker not in connection.execute_wrappers:  # pragma: no branch
        connection.execute_wrappers.insert(0, blocker)


class DjangoReadOnlyError(Exception):
    pass


def blocker(
    execute: Callable[[str, str, bool, dict[str, Any]], Any],
    sql: Any,
    params: str,
    many: bool,
    context: dict[str, Any],
) -> Any:
    if read_only and should_block(sql):
        msg = "Write queries are currently disabled. "
        if ipython_extension_loaded:
            msg += "Enable with '%read_only off' or django_read_only.enable_writes()."
        else:
            msg += "Enable with django_read_only.enable_writes()."
        raise DjangoReadOnlyError(msg)
    return execute(sql, params, many, context)


def should_block(sql: Any) -> bool:
    if isinstance(sql, str):
        pass
    elif HAVE_PSYCOPG and isinstance(sql, Composable):
        sql = sql.as_string(None)
    else:
        return True
    return not sql.lstrip(" \n(").startswith(
        (
            "EXPLAIN ",
            "PRAGMA ",
            "ROLLBACK TO SAVEPOINT ",
            "RELEASE SAVEPOINT ",
            "SAVEPOINT ",
            "SELECT ",
            "SET ",
        )
    ) and sql not in ("BEGIN", "COMMIT", "ROLLBACK")


def enable_writes() -> None:
    global read_only
    read_only = False


def disable_writes() -> None:
    global read_only
    read_only = True


@contextmanager
def temp_writes() -> Generator[None]:
    enable_writes()
    try:
        yield
    finally:
        disable_writes()


def load_ipython_extension(ipython: Any) -> None:
    global ipython_extension_loaded

    from IPython.core.magic import Magics, line_magic, magics_class

    ipython_extension_loaded = True

    @magics_class
    class DjangoReadOnlyMagics(Magics):  # type: ignore [misc]
        @line_magic  # type: ignore [misc]
        def read_only(self, line: str) -> None:
            if line == "on":
                disable_writes()
                print("Write queries disabled.")
            elif line == "off":
                enable_writes()
                print("Write queries enabled.")
            else:
                print(f"Unknown value {line!r}, pass 'on' or 'off'.")

    ipython.register_magics(DjangoReadOnlyMagics)


def unload_ipython_extension(ipython: Any) -> None:
    global ipython_extension_loaded

    ipython_extension_loaded = False
