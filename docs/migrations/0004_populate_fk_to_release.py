# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_release(apps, schema_editor):
    DocumentRelease = apps.get_model('docs', 'DocumentRelease')
    Release = apps.get_model('releases', 'Release')
    for dr in DocumentRelease.objects.exclude(version='dev'):
        try:
            release = Release.objects.get(version=dr.version)
        except Release.DoesNotExist:
            # Hack: we need the actual Release model, specifically
            # its overridden save(), to create a release.
            from releases.models import Release as RealRelease
            release = RealRelease(version=dr.version, date=None)
            release.save()
        # Because of the hack above, we cannot use dr.release = release.
        dr.release_id = release.pk
        dr.save()


def unset_release(apps, schema_editor):
    DocumentRelease = apps.get_model('docs', 'DocumentRelease')
    DocumentRelease.objects.update(release=None)


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0003_add_fk_to_release'),
        ('releases', '0004_make_release_date_nullable'),
    ]

    operations = [
        migrations.RunPython(set_release, unset_release),
    ]
