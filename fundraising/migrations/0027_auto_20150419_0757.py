# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0026_auto_20150419_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='djangohero',
            name='stripe_customer_id',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='email',
            field=models.EmailField(max_length=75, null=True),
            preserve_default=True,
        )
    ]
