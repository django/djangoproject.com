# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0028_auto_20150419_0758'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='interval',
            field=models.CharField(null=True, choices=[('monthly', 'Monthly donation'), ('quarterly', 'Quarterly donation'), ('yearly', 'Yearly donation'), ('onetime', 'One-time donation')], max_length=20),
            preserve_default=True,
        ),
    ]
