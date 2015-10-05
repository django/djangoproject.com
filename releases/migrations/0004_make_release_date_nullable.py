# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0003_populate_release_eol_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='release',
            name='date',
            field=models.DateField(null=True, blank=True, help_text="Leave blank if the release date isn't know yet, typically if you're creating the final release just after the alpha because you want to build docs for the upcoming version.", default=datetime.date.today, verbose_name='Release date'),
        ),
        migrations.AlterField(
            model_name='release',
            name='eol_date',
            field=models.DateField(null=True, blank=True, help_text="Leave blank if the end of life date isn't known yet, typically because it depends on the release date of a later version.", verbose_name='End of life date'),
        ),
        migrations.AlterField(
            model_name='release',
            name='status',
            field=models.CharField(max_length=1, editable=False, choices=[('a', 'alpha'), ('b', 'beta'), ('c', 'release candidate'), ('f', 'final')]),
        ),
    ]
