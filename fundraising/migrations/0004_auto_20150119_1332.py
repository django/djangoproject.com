# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0003_auto_20150119_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='date',
        ),
        migrations.AddField(
            model_name='donation',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='donation',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
