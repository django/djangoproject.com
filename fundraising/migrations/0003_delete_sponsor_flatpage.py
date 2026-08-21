from django.db import migrations


def delete_sponsor_flatpage(apps, schema_editor):
    FlatPage = apps.get_model("flatpages", "FlatPage")
    FlatPage.objects.filter(url="/sponsor/").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("fundraising", "0002_djangohero_approved_booleanfield"),
        ("flatpages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(delete_sponsor_flatpage, migrations.RunPython.noop),
    ]
