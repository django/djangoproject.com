# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def convert_amount(apps, schema_editor):
    # Django 1.7 doesn't check the router.allow_migrate on RunSQL or RunPython
    # operations. So even though we just need to run some SQL we need to run it
    # inside a RunPython function and check the connection alias manually.
    if not schema_editor.connection.alias == 'default':
        return
    cursor = schema_editor.connection.cursor()
    cursor.execute(
        "INSERT INTO fundraising_payment (amount, stripe_charge_id, date, donation_id) "
        "(SELECT amount, stripe_charge_id, created, id FROM fundraising_donation);"
    ),

class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0030_auto_20150604_0608'),
    ]

    operations = [
        migrations.RunPython(convert_amount),
    ]
