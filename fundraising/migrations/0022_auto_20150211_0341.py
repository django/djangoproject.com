# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0021_auto_20150209_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='template',
            field=models.CharField(default=b'fundraising/campaign_default.html', max_length=50),
            preserve_default=True,
        ),
    ]
