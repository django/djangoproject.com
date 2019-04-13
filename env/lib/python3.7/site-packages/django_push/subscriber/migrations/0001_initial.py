# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hub', models.URLField(max_length=1023, verbose_name='Hub')),
                ('topic', models.URLField(max_length=1023, verbose_name='Topic')),
                ('verified', models.BooleanField(default=False, verbose_name='Verified')),
                ('verify_token', models.CharField(max_length=255, verbose_name='Verify Token', blank=True)),
                ('lease_expiration', models.DateTimeField(null=True, verbose_name='Lease expiration', blank=True)),
                ('secret', models.CharField(max_length=255, verbose_name='Secret', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
