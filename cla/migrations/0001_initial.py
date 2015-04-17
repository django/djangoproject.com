# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CCLA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_signed', models.DateField()),
                ('cla', models.FileField(upload_to='cla')),
                ('company_name', models.CharField(max_length=200)),
                ('company_address', models.TextField(blank=True)),
                ('country', models.CharField(max_length=50)),
                ('contact_name', models.CharField(max_length=250)),
                ('contact_email', models.EmailField(max_length=75)),
                ('contact_title', models.CharField(max_length=200)),
                ('telephone', models.CharField(max_length=50, blank=True)),
            ],
            options={
                'verbose_name': 'corporate CLA',
                'verbose_name_plural': 'corporate CLAs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CCLADesignee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateField()),
                ('full_name', models.CharField(max_length=250, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('nickname', models.CharField(max_length=250, blank=True)),
                ('ccla', models.ForeignKey(related_name='designees', to='cla.CCLA')),
            ],
            options={
                'verbose_name': 'CCLA designee',
                'verbose_name_plural': 'CCLA designees',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ICLA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_signed', models.DateField()),
                ('cla', models.FileField(upload_to='cla', blank=True)),
                ('full_name', models.CharField(max_length=250, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('nickname', models.CharField(max_length=250, blank=True)),
                ('telephone', models.CharField(max_length=50, blank=True)),
                ('mailing_address', models.TextField(blank=True)),
                ('country', models.CharField(max_length=50, blank=True)),
                ('user', models.ForeignKey(related_name='iclas', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'individual CLA',
                'verbose_name_plural': 'individual CLAs',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ccladesignee',
            name='icla',
            field=models.ForeignKey(related_name='+', blank=True, to='cla.ICLA', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ccladesignee',
            name='user',
            field=models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
