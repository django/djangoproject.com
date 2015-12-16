# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sorl.thumbnail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corporatemember',
            name='logo',
            field=sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to='corporate-members'),
        ),
    ]
