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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=250)),
                ('billing_name', models.CharField(max_length=250, blank=True, help_text='If different from display name.')),
                ('logo', models.ImageField(blank=True, upload_to='corporate-members', null=True)),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(verbose_name='URL')),
                ('contact_name', models.CharField(max_length=250)),
                ('contact_email', models.EmailField(max_length=254)),
                ('billing_email', models.EmailField(max_length=254, blank=True, help_text='If different from contact email.')),
                ('membership_level', models.IntegerField(choices=[(1, 'Independent consultancy'), (2, 'Small-to-medium business'), (3, 'Large corporation')])),
                ('address', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['display_name'],
            },
        ),
        migrations.CreateModel(
            name='DeveloperMember',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('member_since', models.DateField(default=django.views.generic.dates.timezone_today)),
                ('member_until', models.DateField(blank=True, null=True)),
                ('reason_for_leaving', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('sent_date', models.DateField()),
                ('amount', models.IntegerField(help_text='In integer dollars')),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('member', models.ForeignKey(to='members.CorporateMember')),
            ],
        ),
    ]
