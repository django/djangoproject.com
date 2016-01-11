# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sorl.thumbnail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0006_djangohero_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='InKindDonor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('logo', sorl.thumbnail.fields.ImageField(blank=True, upload_to='fundraising/logos/')),
                ('url', models.URLField(blank=True, verbose_name='URL')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'in-kind hero',
                'verbose_name_plural': 'in-kind heroes',
            },
        ),
    ]
