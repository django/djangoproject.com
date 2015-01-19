# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0002_auto_20150117_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='id',
            field=models.CharField(max_length=12, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
