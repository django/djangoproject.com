# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sorl.thumbnail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0024_djangohero_hero_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='djangohero',
            name='is_amount_displayed',
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_active',
            field=models.BooleanField(help_text='Should donation form be enabled or not?', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='campaign',
            name='is_public',
            field=models.BooleanField(help_text='Should campaign be visible at all?', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='campaign',
            name='template',
            field=models.CharField(max_length=50, default='fundraising/campaign_default.html'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='approved',
            field=models.NullBooleanField(verbose_name='Name, URL, and Logo approved?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='hero_type',
            field=models.CharField(choices=[('individual', 'Individual'), ('organization', 'Organization')], max_length=30, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='is_subscribed',
            field=models.BooleanField(verbose_name='Agreed to being contacted by DSF?', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='is_visible',
            field=models.BooleanField(verbose_name='Agreed to displaying on the fundraising page?', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='logo',
            field=sorl.thumbnail.fields.ImageField(upload_to='fundraising/logos/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='url',
            field=models.URLField(verbose_name='URL', blank=True),
            preserve_default=True,
        ),
    ]
