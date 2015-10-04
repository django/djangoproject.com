# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release',
            name='date',
            field=models.DateField(verbose_name='Release date', default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='release',
            name='eol_date',
            field=models.DateField(null=True, verbose_name='End of life date', blank=True),
        ),
    ]
