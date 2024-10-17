from django.contrib import admin
from django.utils.translation import gettext as _

from .models import Entry, Event


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("headline", "pub_date", "is_active", "is_published", "author")
    list_filter = ("is_active",)
    exclude = ("summary_html", "body_html")
    prepopulated_fields = {"slug": ("headline",)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "content_format":
            formfield.help_text = _("Psst, we have markdown now 🤫")
        if db_field.name == "body":
            formfield.widget.attrs.update(
                {
                    "rows": 60,
                    "style": "font-family: monospace; width: 810px;",
                }
            )
        return formfield


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "headline",
        "external_url",
        "date",
        "location",
        "pub_date",
        "is_active",
        "is_published",
    )
    list_filter = ("is_active",)
