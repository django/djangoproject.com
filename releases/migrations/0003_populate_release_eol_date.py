# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


def set_eol_date(apps, schema_editor):
    Release = apps.get_model('releases', 'Release')
    # Set the EOL date of all releases to the date of the following release
    # except for the final one in the 0 series and in each 1.x series.
    releases = list(Release.objects.all().order_by('major', 'minor', 'micro',
                                                   'status', 'iteration'))
    for previous, current in zip(releases[:-1], releases[1:]):
        if current.major != previous.major:
            continue
        if current.major == 1 and previous.minor != current.minor:
            continue
        previous.eol_date = current.date
        previous.save()
    # Set the EOL date of final releases the 0 series and in each 1.x series.
    for version, eol_date in [
        ('0.96.5', datetime.date(2008, 9, 3)),      # 1.0 release
        ('1.0.4', datetime.date(2010, 5, 17)),      # 1.2 release
        ('1.1.4', datetime.date(2011, 3, 23)),      # 1.3 release
        ('1.2.7', datetime.date(2012, 3, 23)),      # 1.4 release
        ('1.3.7', datetime.date(2013, 2, 26)),      # 1.5 release
        ('1.4.22', datetime.date(2015, 10, 1)),     # end of LTS support
        ('1.5.12', datetime.date(2014, 9, 2)),      # 1.7 release
        ('1.6.11', datetime.date(2015, 4, 1)),      # 1.8 release
        # 1.7.10 and 1.8.5 are still supported at the time of writing.
    ]:
        # This patterns ignores missing releases e.g. during tests.
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
