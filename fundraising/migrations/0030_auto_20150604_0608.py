# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0029_donation_interval'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('amount', models.DecimalField(null=True, max_digits=9, decimal_places=2)),
                ('stripe_charge_id', models.CharField(null=True, max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('donation', models.ForeignKey(to='fundraising.Donation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
