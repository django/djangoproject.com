from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Release

_ARTIFACT_FILE_EXTENSIONS = {"tarball": ".tar.gz", "wheel": ".whl", "checksum": ".txt"}


class ReleaseAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname, accept in _ARTIFACT_FILE_EXTENSIONS.items():
            self.fields[fieldname].widget.attrs["accept"] = accept
        self.fields["is_lts"].label = mark_safe(
            '<abbr title="Long Term Support">LTS</abbr> release'
        )


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["version", "is_lts"]}),
        ("Dates", {"fields": ["date", "eol_date"]}),
        ("Artifacts", {"fields": ["tarball", "wheel", "checksum"]}),
    ]
    form = ReleaseAdminForm
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
