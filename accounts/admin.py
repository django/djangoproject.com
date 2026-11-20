from django import forms
from django.contrib import admin

from .forms import ProfileForm
from .models import Profile, TracAccount


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
    ]
    list_select_related = ["user"]
    search_fields = ["user__username", "name"]
    form = ProfileAdminForm
    autocomplete_fields = ["user"]


class TracAccountAdminForm(forms.ModelForm):
    class Meta:
        model = TracAccount
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["autocomplete"] = "off"


@admin.register(TracAccount)
class TracAccountAdmin(admin.ModelAdmin):
    list_display = [
        "user__username",
        "username",
    ]
    list_select_related = ["user"]
    form = TracAccountAdminForm
    search_fields = ["user__username", "username"]
    autocomplete_fields = ["user"]
