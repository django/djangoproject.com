# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20150823_0321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corporatemember',
            name='formal_name',
            field=models.CharField(max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name='developermember',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
