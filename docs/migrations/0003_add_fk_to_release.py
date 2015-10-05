# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0001_initial'),
        ('docs', '0002_simplify_documentrelease'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentrelease',
            name='release',
            field=models.ForeignKey(null=True, to='releases.Release'),
        ),
        migrations.AlterUniqueTogether(
            name='documentrelease',
            unique_together=set([('lang', 'release'), ('lang', 'version')]),
        ),
    ]
