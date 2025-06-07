from django import forms
from django.contrib import admin

from .models import Release

_ARTIFACTS = ["checksum", "tarball", "wheel"]


class ReleaseAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add `accept` attributes to the artifact file fields to make it a bit
        # easier to pick the right files in the browser's 'filepicker
        extensions = {"tarball": ".tar.gz", "wheel": ".whl", "checksum": ".asc,.txt"}
        for field, accept in extensions.items():
            widget = self.fields[field].widget
            widget.attrs.setdefault("accept", accept)

        self._previous_file_fields = {a: getattr(self.instance, a) for a in _ARTIFACTS}

    # Extending _save_m2m() instead of save() lets us support both save(commit=True/False)
    def _save_m2m(self):
        super()._save_m2m()

        # Delete any files from storage that might have been cleared
        for a in _ARTIFACTS:
            if self._previous_file_fields[a] and not getattr(self.instance, a):
                self._previous_file_fields[a].delete(save=False)


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["version", "is_active", "is_lts"]}),
        ("Dates", {"fields": ["date", "eol_date"]}),
        ("Artifacts", {"fields": ["tarball", "wheel", "checksum"]}),
    ]
    form = ReleaseAdminForm
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
