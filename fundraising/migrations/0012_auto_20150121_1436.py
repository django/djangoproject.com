# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0011_donation_campaign_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='campaign_name',
            field=models.CharField(default='', max_length=100, blank=True),
            preserve_default=False,
        ),
    ]
