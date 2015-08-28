# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import sorl.thumbnail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('goal', models.DecimalField(max_digits=9, decimal_places=2)),
                ('template', models.CharField(max_length=50, default='fundraising/campaign_default.html')),
                ('stretch_goal', models.DecimalField(blank=True, max_digits=9, null=True, decimal_places=2)),
                ('stretch_goal_url', models.URLField(blank=True, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(help_text='Should donation form be enabled or not?', default=False)),
                ('is_public', models.BooleanField(help_text='Should campaign be visible at all?', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DjangoHero',
            fields=[
                ('id', models.CharField(serialize=False, max_length=12, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100)),
                ('logo', sorl.thumbnail.fields.ImageField(blank=True, upload_to='fundraising/logos/')),
                ('url', models.URLField(blank=True, verbose_name='URL')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('hero_type', models.CharField(blank=True, max_length=30, choices=[('individual', 'Individual'), ('organization', 'Organization')])),
                ('is_visible', models.BooleanField(default=False, verbose_name='Agreed to displaying on the fundraising page?')),
                ('is_subscribed', models.BooleanField(default=False, verbose_name='Agreed to being contacted by DSF?')),
                ('approved', models.NullBooleanField(verbose_name='Name, URL, and Logo approved?')),
            ],
            options={
                'verbose_name_plural': 'Django heroes',
                'verbose_name': 'Django hero',
            },
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.CharField(serialize=False, max_length=12, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('interval', models.CharField(blank=True, max_length=20, choices=[('monthly', 'Monthly donation'), ('quarterly', 'Quarterly donation'), ('yearly', 'Yearly donation'), ('onetime', 'One-time donation')])),
                ('subscription_amount', models.DecimalField(blank=True, max_digits=9, null=True, decimal_places=2)),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=100)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100)),
                ('receipt_email', models.EmailField(blank=True, max_length=254)),
                ('campaign', models.ForeignKey(blank=True, to='fundraising.Campaign', null=True)),
                ('donor', models.ForeignKey(to='fundraising.DjangoHero', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('amount', models.DecimalField(max_digits=9, null=True, decimal_places=2)),
                ('stripe_charge_id', models.CharField(blank=True, max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('donation', models.ForeignKey(to='fundraising.Donation')),
            ],
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('author', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(to='fundraising.Campaign', null=True)),
            ],
        ),
    ]
