# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0025_auto_20150419_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='receipt_email',
            field=models.EmailField(null=True, max_length=75),
            preserve_default=True,
        ),
    ]
