from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_migrate_activatedstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupervisedRegistrationProfile',
            fields=[
                ('registrationprofile_ptr', models.OneToOneField(
                    parent_link=True,
                    auto_created=True,
                    on_delete=models.CASCADE,
                    primary_key=True,
                    serialize=False,
                    to='registration.RegistrationProfile')
                 ),
            ],
            bases=('registration.registrationprofile',),
        ),
    ]
