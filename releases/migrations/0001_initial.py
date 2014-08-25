# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('version', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today)),
                ('major', models.PositiveSmallIntegerField(editable=False)),
                ('minor', models.PositiveSmallIntegerField(editable=False)),
                ('micro', models.PositiveSmallIntegerField(editable=False)),
                ('status', models.CharField(max_length=1, editable=False, choices=[('a', 'alpha'), ('b', 'beta'), ('c', 'rc'), ('f', 'final')])),
                ('iteration', models.PositiveSmallIntegerField(editable=False)),
                ('is_lts', models.BooleanField(default=False, verbose_name='Long term support release')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
