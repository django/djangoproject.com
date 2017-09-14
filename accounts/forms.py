from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    """
    A form for editing user profiles.

    Assumes that the Profile instance passed in has an associated User
    object. The view (see views.py) takes care of that.
    """
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Email'})
    )

    class Meta:
        model = Profile
        fields = ['name']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs.setdefault('initial', {}).update({'email': instance.user.email})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if 'email' in self.cleaned_data:
            instance.user.email = self.cleaned_data['email']
            if commit:
                instance.user.save()
        return instance
