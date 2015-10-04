# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentrelease',
            name='docs_subdir',
        ),
        migrations.RemoveField(
            model_name='documentrelease',
            name='scm',
        ),
        migrations.RemoveField(
            model_name='documentrelease',
            name='scm_url',
        ),
    ]
