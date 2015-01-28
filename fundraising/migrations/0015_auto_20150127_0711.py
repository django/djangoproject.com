# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0014_donation_receipt_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='logo',
            field=sorl.thumbnail.fields.ImageField(upload_to=b'fundraising/logos/', blank=True),
            preserve_default=True,
        ),
    ]
