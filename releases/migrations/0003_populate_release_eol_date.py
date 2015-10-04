# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


def set_eol_date(apps, schema_editor):
    Release = apps.get_model('releases', 'Release')
    # List of EOL dates for releases for which docs are published.
    for version, eol_date in [
        ('1.4', datetime.date(2015, 10, 1)),
        ('1.5', datetime.date(2014, 9, 2)),
        ('1.6', datetime.date(2015, 4, 1)),
    ]:
        Release.objects.filter(version=version).update(eol_date=eol_date)

def unset_eol_date(apps, schema_editor):
    Release = apps.get_model('releases', 'Release')
    Release.objects.update(eol_date=None)


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0002_release_eol_date'),
    ]

    operations = [
        migrations.RunPython(set_eol_date, unset_eol_date),
    ]
