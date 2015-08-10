# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import crypto


def copy_stripe_id_to_hero(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    Donation = apps.get_model("fundraising", "Donation")
    DjangoHero = apps.get_model("fundraising", "DjangoHero")

    with_out_hero = Donation.objects.filter(donor=None)
    with_hero = Donation.objects.filter(donor__isnull=False)

    for donation in with_out_hero:
        DjangoHero.objects.create(
            id=crypto.get_random_string(length=12),
            email=donation.receipt_email,
            stripe_customer_id=donation.stripe_customer_id,
        )

    for donation in with_hero.select_related('donor'):
        hero = donation.donor
        hero.stripe_customer_id = donation.stripe_customer_id
        hero.save()


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0027_auto_20150419_0757'),
    ]

    operations = [
        migrations.RunPython(copy_stripe_id_to_hero),
    ]
