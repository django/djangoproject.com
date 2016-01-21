# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('feed_url', models.URLField(unique=True, max_length=500)),
                ('public_url', models.URLField(max_length=500)),
                ('approval_status', models.CharField(default='P', max_length=1, choices=[('P', 'Pending'), ('D', 'Denied'), ('A', 'Approved')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('link', models.URLField(max_length=500)),
                ('summary', models.TextField(blank=True)),
                ('date_modified', models.DateTimeField()),
                ('guid', models.CharField(unique=True, max_length=500, db_index=True)),
                ('feed', models.ForeignKey(to='aggregator.Feed', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-date_modified',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=250)),
                ('can_self_add', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='feed',
            name='feed_type',
            field=models.ForeignKey(to='aggregator.FeedType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='feed',
            name='owner',
            field=models.ForeignKey(related_name='owned_feeds', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]
