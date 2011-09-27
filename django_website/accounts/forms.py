from __future__ import absolute_import
from django import forms
from registration.forms import RegistrationFormUniqueEmail
from .models import Profile

class RegistrationForm(RegistrationFormUniqueEmail):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields["tos"]

class ProfileForm(forms.ModelForm):
    """
    A form for editing user profiles.

    Assumes that the Profile instance passed in has an associated User
    object. The view (see views.py) takes care of tha
    """
    class Meta(object):
        model = Profile
        fields = ['name']
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs.setdefault('initial', {}).update({'email': instance.user.email})
        super(ProfileForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ProfileForm, self).save(commit=commit)
        if 'email' in self.cleaned_data:
            instance.user.email = self.cleaned_data['email']
            if commit:
                instance.user.save()
        return instance
