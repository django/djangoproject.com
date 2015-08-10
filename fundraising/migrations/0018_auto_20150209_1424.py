# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0017_auto_20150209_1405'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='campaign_name',
        ),
        migrations.AddField(
            model_name='donation',
            name='campaign',
            field=models.ForeignKey(to='fundraising.Campaign', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testimonial',
            name='campaign',
            field=models.ForeignKey(to='fundraising.Campaign', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='campaign',
            name='template',
            field=models.CharField(default=b'fundraising/campaign_default.html', max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
