from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("docs", "0005_document_config"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="metadata",
            field=models.JSONField(default=dict),
        ),
    ]
