# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # Remove all recurring donations from their campaign. They'll appear under
    # a separate "recurring donations" page.
    Donation = apps.get_model('fundraising', 'Donation')
    Donation.objects.exclude(interval='').update(campaign=None)


def reverse_func(apps, schema_editor):
    Donation = apps.get_model('fundraising', 'Donation')
    Donation.objects.filter(campaign__isnull=True).update(campaign=1)


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0001_squashed_0037_auto_20150709_1619'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
