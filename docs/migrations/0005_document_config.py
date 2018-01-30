from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0004_add_release_title_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='config',
            field=models.SlugField(default='simple'),
        ),
    ]
