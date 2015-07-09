# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0034_auto_20150702_0241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='donation',
            name='interval',
            field=models.CharField(blank=True, choices=[('monthly', 'Monthly donation'), ('quarterly', 'Quarterly donation'), ('yearly', 'Yearly donation'), ('onetime', 'One-time donation')], max_length=20),
        ),
        migrations.AlterField(
            model_name='donation',
            name='receipt_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='donation',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='donation',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='payment',
            name='stripe_charge_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
