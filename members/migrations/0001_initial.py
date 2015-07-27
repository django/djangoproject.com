# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.views.generic.dates
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorporateMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('display_name', models.CharField(max_length=250)),
                ('formal_name', models.CharField(max_length=250)),
                ('logo', models.ImageField(blank=True, upload_to='corporate-members', null=True)),
                ('description', models.TextField()),
                ('url', models.URLField()),
                ('contact_email', models.EmailField(max_length=75)),
                ('billing_email', models.EmailField(max_length=75)),
                ('initial_contact_date', models.DateField(default=django.views.generic.dates.timezone_today)),
                ('membership_level', models.IntegerField(choices=[(1, 'Independent consultancy'), (2, 'Small-to-medium business'), (3, 'Large corporation')])),
                ('membership_start', models.DateField()),
                ('membership_expires', models.DateField()),
                ('address', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeveloperMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=75)),
                ('member_since', models.DateField(default=django.views.generic.dates.timezone_today)),
                ('member_until', models.DateField(blank=True, null=True)),
                ('reason_for_leaving', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
