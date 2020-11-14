from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('fundraising', '0001_squashed_0007_inkinddonor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djangohero',
            name='approved',
            field=models.BooleanField(null=True, verbose_name='Name, URL, and Logo approved?'),
        ),
    ]
