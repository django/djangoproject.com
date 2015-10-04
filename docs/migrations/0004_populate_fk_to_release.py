# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_release(apps, schema_editor):
    DocumentRelease = apps.get_model('docs', 'DocumentRelease')
    Release = apps.get_model('releases', 'Release')
    for dr in DocumentRelease.objects.all():
        if dr.version == 'dev':
            continue
        dr.release = Release.objects.get(pk=dr.version)
        dr.save()


def unset_release(apps, schema_editor):
    DocumentRelease = apps.get_model('docs', 'DocumentRelease')
    DocumentRelease.objects.update(release=None)


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0003_add_fk_to_release'),
        ('releases', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_release, unset_release),
    ]
