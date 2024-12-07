from django.contrib import admin

from .models import Release


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["version", "is_active", "is_lts"]}),
        ("Dates", {"fields": ["date", "eol_date"]}),
        ("Artifacts", {"fields": ["tarball", "wheel", "checksum"]}),
    ]
    list_display = (
        "version",
        "show_is_published",
        "is_lts",
        "date",
        "eol_date",
        "major",
        "minor",
        "micro",
        "show_status",
        "iteration",
    )
    list_filter = ("status", "is_lts", "is_active")
    ordering = ("-major", "-minor", "-micro", "-status", "-iteration")

    def get_form(self, request, obj=None, change=False, **kwargs):
        form_class = super().get_form(request, obj=obj, change=change, **kwargs)
        # Add `accept` attributes to the artifact file fields to make it a bit
        # easier to pick the right files in the browser's 'filepicker
        extensions = {"tarball": ".tar.gz", "wheel": ".whl", "checksum": ".asc,.txt"}
        for field, accept in extensions.items():
            widget = form_class.base_fields[field].widget
            widget.attrs.setdefault("accept", accept)
        return form_class

    @admin.display(
        description="status",
        ordering="status",
    )
    def show_status(self, obj):
        return obj.get_status_display()

    @admin.display(
        boolean=True,
        description="Published?",
        ordering="is_active",
    )
    def show_is_published(self, obj):
        return obj.is_published
