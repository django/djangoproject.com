# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0006_auto_20150119_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='stripe_charge_id',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='donation',
            name='stripe_customer_id',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
