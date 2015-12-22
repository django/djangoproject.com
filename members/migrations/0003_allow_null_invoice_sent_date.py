# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_corporatemember_logo_to_sorlimagefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corporatemember',
            name='membership_level',
            field=models.IntegerField(choices=[(1, 'Silver'), (2, 'Gold'), (3, 'Platinum')]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='sent_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
