# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def null_to_blank(apps, schema_editor):
    DjangoHero = apps.get_model('fundraising', 'DjangoHero')
    DjangoHero.objects.filter(stripe_customer_id__isnull=True).update(stripe_customer_id='')
    Payment = apps.get_model('fundraising', 'Payment')
    Payment.objects.filter(stripe_charge_id__isnull=True).update(stripe_charge_id='')
    Donation = apps.get_model('fundraising', 'Donation')
    fields = ['interval', 'receipt_email', 'stripe_customer_id', 'stripe_subscription_id']
    for field in fields:
        Donation.objects.filter(**{'%s__isnull' % field: True}).update(**{field: ''})


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0033_auto_20150611_0750'),
    ]

    operations = [
        migrations.RunPython(null_to_blank)
    ]
