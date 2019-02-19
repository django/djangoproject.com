#!/bin/sh

# Update translations from Transifex for the supported languages, and remove
# the source location references (to help keep the diff noise down). Adapted from:
# https://github.com/django/django-docs-translations/blob/stable/2.1.x/manage_translations.py

set -ex

LANGUAGES="el es fr id ja ko pl pt_BR zh_CN zh_TW"

LOCALE_DIRS="dashboard/locale/ docs/locale/ locale/"

for LANG in $LANGUAGES; do
    tx pull -f -l $LANG --minimum-perc=5
    for DIR in $LOCALE_DIRS; do
        PO_FILE="$DIR$LANG/LC_MESSAGES/django.po"
        msgcat --no-location -o $PO_FILE $PO_FILE
    done
done
