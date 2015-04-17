# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0008_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='djangohero',
            name='approved',
            field=models.NullBooleanField(verbose_name=b'Name, URL, and Logo approved?'),
            preserve_default=True,
        ),
    ]
