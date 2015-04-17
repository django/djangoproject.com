# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
            ],
            options={
                'db_table': 'attachment_django_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
            ],
            options={
                'db_table': 'component',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
            ],
            options={
                'db_table': 'milestone',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
            ],
            options={
                'db_table': 'revision',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
            ],
            options={
                'db_table': 'ticket',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketChange',
            fields=[
            ],
            options={
                'ordering': ['_time'],
                'db_table': 'ticket_change',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketCustom',
            fields=[
            ],
            options={
                'db_table': 'ticket_custom',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
            ],
            options={
                'db_table': 'version',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wiki',
            fields=[
            ],
            options={
                'db_table': 'wiki_django_view',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
