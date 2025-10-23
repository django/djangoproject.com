from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .forms import ProfileForm
from .models import Profile


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bio"].widget.attrs["maxlength"] = ProfileForm.base_fields[
            "bio"
        ].max_length
        self.fields["bio"].help_text = ProfileForm.base_fields["bio"].help_text


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user__username",
        "name",
        "trac_username",
    ]
    list_select_related = ["user"]
    search_fields = ["user__username", "name", "trac_username"]
    form = ProfileAdminForm
    autocomplete_fields = ["user"]
