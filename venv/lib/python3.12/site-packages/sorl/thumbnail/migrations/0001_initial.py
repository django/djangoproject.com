from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KVStore',
            fields=[
                ('key', models.CharField(serialize=False,
                                         db_column='key',
                                         max_length=200,
                                         primary_key=True)),
                ('value', models.TextField()),
            ],
        ),
    ]
