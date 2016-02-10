# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('position', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('measurement', models.BigIntegerField()),
                ('content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-timestamp'],
                'get_latest_by': 'timestamp',
                'verbose_name_plural': 'data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GithubItemCountMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('slug', models.SlugField()),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('show_on_dashboard', models.BooleanField(default=True)),
                ('show_sparkline', models.BooleanField(default=True)),
                ('period', models.CharField(default='instant', max_length=15, choices=[('instant', 'Instant'), ('daily', 'Daily'), ('weekly', 'Weekly')])),
                ('unit', models.CharField(max_length=100)),
                ('unit_plural', models.CharField(max_length=100)),
                ('api_url', models.URLField(max_length=1000)),
                ('link_url', models.URLField(max_length=1000)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='dashboard.Category', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JenkinsFailuresMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('slug', models.SlugField()),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('show_on_dashboard', models.BooleanField(default=True)),
                ('show_sparkline', models.BooleanField(default=True)),
                ('period', models.CharField(default='instant', max_length=15, choices=[('instant', 'Instant'), ('daily', 'Daily'), ('weekly', 'Weekly')])),
                ('unit', models.CharField(max_length=100)),
                ('unit_plural', models.CharField(max_length=100)),
                ('jenkins_root_url', models.URLField(help_text='E.g. http://ci.djangoproject.com/', max_length=1000, verbose_name='Jenkins instance root URL')),
                ('build_name', models.CharField(help_text='E.g. Django Python3', max_length=100)),
                ('is_success_cnt', models.BooleanField(
                    default=False,
                    help_text='E.g. if there are 50 tests of which 30 are failing the value of this metric will be 20 (or 40%.)',
                    verbose_name='Should the metric be a value representing success ratio?',
                )),
                ('is_percentage', models.BooleanField(
                    default=False,
                    help_text='E.g. if there are 50 tests of which 30 are failing the value of this metric will be 60%.',
                    verbose_name='Should the metric be a percentage value?',
                )),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='dashboard.Category', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RSSFeedMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('slug', models.SlugField()),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('show_on_dashboard', models.BooleanField(default=True)),
                ('show_sparkline', models.BooleanField(default=True)),
                ('period', models.CharField(default='instant', max_length=15, choices=[('instant', 'Instant'), ('daily', 'Daily'), ('weekly', 'Weekly')])),
                ('unit', models.CharField(max_length=100)),
                ('unit_plural', models.CharField(max_length=100)),
                ('feed_url', models.URLField(max_length=1000)),
                ('link_url', models.URLField(max_length=1000)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='dashboard.Category', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TracTicketMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('slug', models.SlugField()),
                ('position', models.PositiveSmallIntegerField(default=1)),
                ('show_on_dashboard', models.BooleanField(default=True)),
                ('show_sparkline', models.BooleanField(default=True)),
                ('period', models.CharField(default='instant', max_length=15, choices=[('instant', 'Instant'), ('daily', 'Daily'), ('weekly', 'Weekly')])),
                ('unit', models.CharField(max_length=100)),
                ('unit_plural', models.CharField(max_length=100)),
                ('query', models.TextField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='dashboard.Category', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
