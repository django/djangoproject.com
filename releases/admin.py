from django.contrib import admin

from .models import Release


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "is_lts",
        "date",
        "eol_date",
        "major",
        "minor",
        "micro",
        "show_status",
        "iteration",
    )
    list_filter = ("status", "is_lts")
    ordering = ("-major", "-minor", "-micro", "-status", "-iteration")

    @admin.display(
        description="status",
        ordering="status",
    )
    def show_status(self, obj):
        return obj.get_status_display()
