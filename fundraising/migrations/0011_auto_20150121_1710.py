# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0010_auto_20150121_0818'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='djangohero',
            options={'verbose_name': 'Django hero', 'verbose_name_plural': 'Django heroes'},
        ),
    ]
