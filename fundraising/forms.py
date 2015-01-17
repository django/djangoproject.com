from django import forms

from .models import DjangoHero

class AddDjangoHeroForm(forms.ModelForm):
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'required', 'placeholder': 'E-mail address'}),
        help_text='We ask for email because we need to match your donation with information from this form.')
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'required', 'placeholder': 'Your name or name of your organization'}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Should we link your name to somewhere? Tell us where'}))
    logo = forms.FileField(required=False, help_text='If you donated at least $200, you can submit your logo and we will display it too.')
    is_visible = forms.BooleanField(required=False, label='Yes, I want this informations to be displayed on the Fundraising page.')
    is_subscribed = forms.BooleanField(required=False, label='Django Software Foundation can ocasionally inform me about fundraising.')
    is_amount_displayed = forms.BooleanField(required=False, label='Yes, information about the amount of my donation can be public.')

    class Meta:
        model = DjangoHero
        fields = ('email', 'name', 'url', 'logo', 'is_visible', 'is_amount_displayed', 'is_subscribed')
