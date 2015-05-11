# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sorl.thumbnail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0014_donation_receipt_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='logo',
            field=sorl.thumbnail.fields.ImageField(upload_to='fundraising/logos/', blank=True),
            preserve_default=True,
        ),
    ]
