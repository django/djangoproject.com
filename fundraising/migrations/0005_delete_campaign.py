# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0004_remove_campaign_fks'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Campaign',
        ),
    ]
