# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('headline', models.CharField(max_length=200)),
                ('external_url', models.URLField()),
                ('date', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(
                    default=False,
                    help_text=(
                        "Tick to make this event live (see also the publication "
                        "date). Note that administrators (like yourself) are "
                        "allowed to preview inactive events whereas the "
                        "general public aren't."
                    ),
                )),
                ('pub_date', models.DateTimeField(
                    help_text='For an event to be published, it must be active and its publication date must be in the past.',
                    verbose_name='Publication date',
                )),
            ],
            options={
                'ordering': ('-pub_date',),
                'get_latest_by': 'pub_date',
            },
            bases=(models.Model,),
        ),
    ]
