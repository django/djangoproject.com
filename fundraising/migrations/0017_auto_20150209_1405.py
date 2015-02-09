# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0016_campaign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='template',
            field=models.CharField(default=b'fundraising/campaign_default.html', help_text=b'Leave it empty to default to fundraising/campaign_default.html', max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
