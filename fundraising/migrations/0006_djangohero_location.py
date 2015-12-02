# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0005_delete_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='djangohero',
            name='location',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
