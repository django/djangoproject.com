# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0023_donation_stripe_subscription_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='djangohero',
            name='hero_type',
            field=models.CharField(blank=True, max_length=30, choices=[(b'individual', b'Individual'), (b'organization', b'Organization')]),
            preserve_default=True,
        ),
    ]
