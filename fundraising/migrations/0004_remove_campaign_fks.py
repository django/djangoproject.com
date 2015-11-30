# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0003_payment_stripe_charge_id_unique'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='campaign',
        ),
    ]
