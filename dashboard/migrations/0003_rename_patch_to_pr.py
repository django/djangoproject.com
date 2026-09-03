from django.db import migrations

CATEGORY_RENAMES = {
    # old name: new name
    "Patches": "Pull requests",
}

TRACMETRIC_RENAMES = {
    # old name: new name
    "Patches needing review": "Tickets with PRs needing review",
    "Doc. patches needing review": "Doc. tickets with PRs needing review",
}

CATEGORY_CHANGES = {
    # Metric name: (old category, new category)
    "\"Easy\" tickets": ("Patches", "Accepted tickets by type"),
}


def _reverse(d):
    """
    Reverse the given dict (values become keys and vice-versa).
    """
    return {v: k for k, v in d.items()}


def rename(apps, schema_editor):
    Category = apps.get_model("dashboard", "Category")
    TracTicketMetric = apps.get_model("dashboard", "TracTicketMetric")

    for metric, (old, new) in CATEGORY_CHANGES.items():
        new_category = Category.objects.filter(name=new).first()
        if not new_category:
            continue
        metrics = TracTicketMetric.objects.filter(name=metric, category__name=old)
        metrics.update(category=new_category)

    for old, new in CATEGORY_RENAMES.items():
        Category.objects.filter(name=old).update(name=new)

    for old, new in TRACMETRIC_RENAMES.items():
        TracTicketMetric.objects.filter(name=old).update(name=new)


def rename_backwards(apps, schema_editor):
    Category = apps.get_model("dashboard", "Category")
    TracTicketMetric = apps.get_model("dashboard", "TracTicketMetric")

    for old, new in _reverse(TRACMETRIC_RENAMES).items():
        TracTicketMetric.objects.filter(name=old).update(name=new)

    for old, new in _reverse(CATEGORY_RENAMES).items():
        Category.objects.filter(name=old).update(name=new)

    for metric, (new, old) in CATEGORY_CHANGES.items():
        new_category = Category.objects.filter(name=new).first()
        if not new_category:
            continue
        metrics = TracTicketMetric.objects.filter(name=metric, category__name=old)
        metrics.update(category=new_category)


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_delete_rssfeedmetric_create_githubsearchcountmetric'),
    ]

    operations = [
        migrations.RunPython(rename, rename_backwards),
    ]
