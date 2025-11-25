"""
This file provides zest.releaser entrypoints using when releasing new
django-countries versions.
"""

import os

from django.core.management import call_command
from zest.releaser.utils import ask, execute_command  # type: ignore

import django_countries


def translations(data) -> None:
    if data["name"] != "django-countries":
        return

    if not ask("Pull translations from transifex and compile", default=True):
        return

    execute_command(["tx", "pull", "-a", "--minimum-perc=60"])
    _cwd = os.getcwd()
    os.chdir(os.path.dirname(django_countries.__file__))
    try:
        call_command("compilemessages")
        execute_command(["git", "add", "locale"])
    finally:
        os.chdir(_cwd)


if __name__ == "__main__":
    translations({"name": "django-countries"})
