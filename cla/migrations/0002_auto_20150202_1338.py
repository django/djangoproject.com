# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cla', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ccla',
            name='contact_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='ccladesignee',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='icla',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]
