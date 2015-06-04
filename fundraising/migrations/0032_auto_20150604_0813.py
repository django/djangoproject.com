# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0031_auto_20150604_0813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='amount',
            new_name='subscription_amount',
        ),
        migrations.AlterField(
            model_name='donation',
            name='subscription_amount',
            field=models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=9),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='donation',
            name='stripe_charge_id',
        ),
    ]
