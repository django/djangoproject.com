from django import forms
from django.db import transaction
from django.db.models import ProtectedError
from django.utils.translation import gettext_lazy as _

from .models import Profile


class ProfileForm(forms.ModelForm):
    """
    A form for editing user profiles.

    Assumes that the Profile instance passed in has an associated User
    object. The view (see views.py) takes care of that.
    """

    name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": _("Name")})
    )
    email = forms.EmailField(
        required=False, widget=forms.TextInput(attrs={"placeholder": _("Email")})
    )

    class Meta:
        model = Profile
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance:
            kwargs.setdefault("initial", {}).update({"email": instance.user.email})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if "email" in self.cleaned_data:
            instance.user.email = self.cleaned_data["email"]
            if commit:
                instance.user.save()
        return instance


class DeleteProfileForm(forms.Form):
    """
    A form for deleting the request's user and their associated data.

    This form has no fields, it's used as a container for validation and deletion
    logic.
    """

    class InvalidFormError(Exception):
        pass

    def __init__(self, *args, user=None, **kwargs):
        if user.is_anonymous:
            raise TypeError("DeleteProfileForm only accepts actual User instances")
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user.is_staff:
            # Prevent potentially deleting some important history (admin.LogEntry)
            raise forms.ValidationError(_("Staff users cannot be deleted"))
        return cleaned_data

    def add_errors_from_protectederror(self, exception):
        """
        Convert the given ProtectedError exception object into validation
        errors on the instance.
        """
        self.add_error(None, _("User has protected data and cannot be deleted"))

    @transaction.atomic()
    def delete(self):
        """
        Delete the form's user (self.instance).
        """
        if not self.is_valid():
            raise self.InvalidFormError(
                "DeleteProfileForm.delete() can only be called on valid forms"
            )

        try:
            self.user.delete()
        except ProtectedError as e:
            self.add_errors_from_protectederror(e)
            return None
        return self.user
