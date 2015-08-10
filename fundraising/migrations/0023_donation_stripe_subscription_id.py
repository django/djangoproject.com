# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0022_auto_20150211_0341'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='stripe_subscription_id',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
