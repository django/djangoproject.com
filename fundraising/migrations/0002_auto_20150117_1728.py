# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(null=True, max_digits=9, decimal_places=2)),
                ('date', models.DateTimeField()),
                ('donor', models.ForeignKey(to='fundraising.DjangoHero', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='is_amount_displayed',
            field=models.BooleanField(default=False, verbose_name=b'Agreed to disclose amount of donation?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='is_subscribed',
            field=models.BooleanField(default=False, verbose_name=b'Agreed to being contacted by DSF?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='is_visible',
            field=models.BooleanField(default=False, verbose_name=b'Agreed to displaying on the fundraising page?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='djangohero',
            name='logo',
            field=models.ImageField(upload_to=b'fundraising/logos/', blank=True),
            preserve_default=True,
        ),
    ]
