# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corporatemember',
            name='billing_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='corporatemember',
            name='contact_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='developermember',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
