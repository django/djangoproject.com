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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('display_name', models.CharField(max_length=250)),
                ('formal_name', models.CharField(max_length=250)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='corporate-members')),
                ('description', models.TextField()),
                ('url', models.URLField()),
                ('contact_email', models.EmailField(max_length=254)),
                ('billing_email', models.EmailField(max_length=254)),
                ('initial_contact_date', models.DateField(default=django.views.generic.dates.timezone_today)),
                ('membership_level', models.IntegerField(choices=[(1, 'Independent consultancy'), (2, 'Small-to-medium business'), (3, 'Large corporation')])),
                ('membership_start', models.DateField()),
                ('membership_expires', models.DateField()),
                ('address', models.TextField()),
                ('is_approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DeveloperMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=254)),
                ('member_since', models.DateField(default=django.views.generic.dates.timezone_today)),
                ('member_until', models.DateField(blank=True, null=True)),
                ('reason_for_leaving', models.TextField(blank=True)),
            ],
        ),
    ]
