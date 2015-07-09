# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0036_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='receipt_email',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]
