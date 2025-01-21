from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0007_alter_validators_add_error_messages"),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop),
    ]
