# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0033_auto_20150611_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='stripe_customer_id',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donation',
            name='interval',
            field=models.CharField(blank=True, choices=[('monthly', 'Monthly donation'), ('quarterly', 'Quarterly donation'), ('yearly', 'Yearly donation'), ('onetime', 'One-time donation')], default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donation',
            name='receipt_email',
            field=models.EmailField(blank=True, default='', max_length=75),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donation',
            name='stripe_customer_id',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donation',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='stripe_charge_id',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
    ]
