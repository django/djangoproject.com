# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0015_auto_20150127_0711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='donation',
            name='receipt_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
