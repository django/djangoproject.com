# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0015_auto_20150127_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('goal', models.DecimalField(max_digits=9, decimal_places=2)),
                ('template', models.CharField(max_length=50)),
                ('stretch_goal', models.DecimalField(max_digits=9, decimal_places=2, blank=True)),
                ('stretch_goal_url', models.URLField(blank=True)),
                ('start_date', models.DateTimeField(blank=True)),
                ('end_date', models.DateTimeField(blank=True)),
                ('is_active', models.BooleanField(default=False, help_text=b'Should donation form be enabled or not?')),
                ('is_public', models.BooleanField(default=False, help_text=b'Should campaign be visible at all?')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
