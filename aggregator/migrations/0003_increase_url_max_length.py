from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aggregator", "0002_add_feed_approver_auth_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feed",
            name="public_url",
            field=models.URLField(max_length=1023),
        ),
        migrations.AlterField(
            model_name="feeditem",
            name="link",
            field=models.URLField(max_length=1023),
        ),
    ]
