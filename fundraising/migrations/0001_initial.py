# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DjangoHero',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('logo', models.ImageField(upload_to=b'', blank=True)),
                ('url', models.URLField(blank=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('is_visible', models.BooleanField(default=False)),
                ('is_subscribed', models.BooleanField(default=False)),
                ('is_amount_displayed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
