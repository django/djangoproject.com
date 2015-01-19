# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0005_auto_20150119_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='id',
            field=models.CharField(max_length=12, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
