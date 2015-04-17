# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0010_auto_20150121_0818'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='campaign_name',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
