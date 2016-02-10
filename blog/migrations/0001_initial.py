# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('headline', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique_for_date='pub_date')),
                ('is_active', models.BooleanField(
                    default=False,
                    help_text=(
                        "Tick to make this entry live (see also the publication "
                        "date). Note that administrators (like yourself) are "
                        "allowed to preview inactive entries whereas the "
                        "general public aren't."
                    ),
                )),
                ('pub_date', models.DateTimeField(
                    help_text='For an entry to be published, it must be active and its publication date must be in the past.',
                    verbose_name='Publication date',
                )),
                ('content_format', models.CharField(max_length=50, choices=[('reST', 'reStructuredText'), ('html', 'Raw HTML')])),
                ('summary', models.TextField()),
                ('summary_html', models.TextField()),
                ('body', models.TextField()),
                ('body_html', models.TextField()),
                ('author', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('-pub_date',),
                'db_table': 'blog_entries',
                'verbose_name_plural': 'entries',
                'get_latest_by': 'pub_date',
            },
            bases=(models.Model,),
        ),
    ]
