# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_allow_null_invoice_sent_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatemember',
            name='notes',
            field=models.TextField(help_text='Not displayed publicly.', blank=True),
        ),
    ]
