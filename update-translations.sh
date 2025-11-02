#!/bin/sh

# Script to update translations and remove the source location references (to help keep the
# diff noise down). Adapted from:
# https://github.com/django/django-docs-translations/blob/stable/2.1.x/manage_translations.py

set -ex

# Any non-app directories added here must also be added to settings.LOCALE_PATHS
LOCALE_DIRS="dashboard/locale/ docs/locale/ locale/"

tx pull -a -f --minimum-perc=70

for DIR in $LOCALE_DIRS; do
    for PO_FILE in $(find $DIR -name django.po -not -path en/); do
        msgcat --no-location -o $PO_FILE $PO_FILE
    done
done
