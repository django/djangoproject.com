# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20150726_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatemember',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
