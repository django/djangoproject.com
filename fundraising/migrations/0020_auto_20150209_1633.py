# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0019_data_migration_for_campaign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='campaign',
            field=models.ForeignKey(blank=True, to='fundraising.Campaign', null=True),
            preserve_default=True,
        ),
    ]
