from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_supervisedregistrationprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationprofile',
            name='activation_key',
            field=models.CharField(max_length=64, verbose_name='activation key'),
        ),
    ]
