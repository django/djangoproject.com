# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0004_populate_fk_to_release'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='documentrelease',
            unique_together=set([('lang', 'release')]),
        ),
        migrations.RemoveField(
            model_name='documentrelease',
            name='version',
        ),
    ]
