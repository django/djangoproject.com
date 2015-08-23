# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='corporatemember',
            options={'ordering': ['display_name']},
        ),
        migrations.AlterModelOptions(
            name='developermember',
            options={'ordering': ['name']},
        ),
    ]
