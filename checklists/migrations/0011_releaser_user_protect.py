"""Change Releaser.user on_delete from CASCADE to PROTECT.

This ensures that deleting a User who has Releaser records will fail at the
database level, protecting release-signing key metadata from accidental deletion.

Used by the delete_unactivated_users management command to guarantee that only
User, Profile, and RegistrationProfile objects are deleted.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("checklists", "0010_securityissue_unsupported_series"),
    ]

    operations = [
        migrations.AlterField(
            model_name="releaser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
