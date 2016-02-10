# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


def forwards_func(apps, schema_editor):
    if schema_editor.connection.alias == 'default':
        apps.get_model('auth', 'Group').objects.create(name=settings.FEED_APPROVERS_GROUP_NAME)


def reverse_func(apps, schema_editor):
    if schema_editor.connection.alias == 'default':
        apps.get_model('auth', 'Group').objects.get(name=settings.FEED_APPROVERS_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
