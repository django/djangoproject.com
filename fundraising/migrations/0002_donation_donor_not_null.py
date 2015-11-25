# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0001_squashed_0037_auto_20150709_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(to='fundraising.DjangoHero'),
        ),
    ]
