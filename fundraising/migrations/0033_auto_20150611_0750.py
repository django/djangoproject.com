# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_onetime_subscriptions(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    Donation = apps.get_model("fundraising", "Donation")
    Donation.objects.filter(interval="onetime").update(subscription_amount=None)


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0032_auto_20150604_0813'),
    ]

    operations = [
        migrations.RunPython(update_onetime_subscriptions),
    ]
