# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0002_donation_donor_not_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='stripe_charge_id',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
