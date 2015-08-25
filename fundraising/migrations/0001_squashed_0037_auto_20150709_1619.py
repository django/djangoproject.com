# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
import sorl.thumbnail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ('fundraising', '0001_initial'),
        ('fundraising', '0002_auto_20150117_1728'),
        ('fundraising', '0003_auto_20150119_1332'),
        ('fundraising', '0004_auto_20150119_1332'),
        ('fundraising', '0005_auto_20150119_1333'),
        ('fundraising', '0006_auto_20150119_1335'),
        ('fundraising', '0007_auto_20150119_1335'),
        ('fundraising', '0003_auto_20150119_1842'),
        ('fundraising', '0008_merge'),
        ('fundraising', '0009_djangohero_approved'),
        ('fundraising', '0010_auto_20150121_0818'),
        ('fundraising', '0011_donation_campaign_name'),
        ('fundraising', '0012_auto_20150121_1436'),
        ('fundraising', '0011_auto_20150121_1710'),
        ('fundraising', '0013_merge'),
        ('fundraising', '0014_donation_receipt_email'),
        ('fundraising', '0015_auto_20150127_0711'),
        ('fundraising', '0016_campaign'),
        ('fundraising', '0017_auto_20150209_1405'),
        ('fundraising', '0018_auto_20150209_1424'),
        ('fundraising', '0019_data_migration_for_campaign'),
        ('fundraising', '0020_auto_20150209_1633'),
        ('fundraising', '0021_auto_20150209_1704'),
        ('fundraising', '0022_auto_20150211_0341'),
        ('fundraising', '0023_donation_stripe_subscription_id'),
        ('fundraising', '0024_djangohero_hero_type'),
        ('fundraising', '0025_auto_20150419_0655'),
        ('fundraising', '0026_auto_20150419_0727'),
        ('fundraising', '0027_auto_20150419_0757'),
        ('fundraising', '0028_auto_20150419_0758'),
        ('fundraising', '0029_donation_interval'),
        ('fundraising', '0030_auto_20150604_0608'),
        ('fundraising', '0031_auto_20150604_0813'),
        ('fundraising', '0032_auto_20150604_0813'),
        ('fundraising', '0033_auto_20150611_0750'),
        ('fundraising', '0034_auto_20150702_0241'),
        ('fundraising', '0035_auto_20150709_1443'),
        ('fundraising', '0016_auto_20150202_1338'),
        ('fundraising', '0036_merge'),
        ('fundraising', '0037_auto_20150709_1619'),
    ]

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
