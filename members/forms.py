from django import forms

from .models import CorporateMember


class CorporateMemberSignUpForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkbox_fields = []
        self.radio_select_fields = []
        self.label_fields = []
        for name, field in self.fields.items():
            help_text = field.help_text
            if help_text:
                help_text = ' (' + help_text + ')'
                self.fields[name].help_text = ''
            self.fields[name].widget.attrs = {'placeholder': field.label + help_text}

            if isinstance(field.widget, forms.CheckboxInput):
                self.checkbox_fields.append(name)
            elif isinstance(field.widget, forms.RadioSelect):
                self.radio_select_fields.append(name)
            elif isinstance(field.widget, (forms.FileInput, forms.Select)):
                self.label_fields.append(name)

        self.fields['billing_name'].widget.attrs['placeholder'] = (
            "Billing name (If different from above name)."
        )
        self.fields['billing_name'].help_text = (
            "For example, this might be your full registered company name."
        )
        self.fields['display_name'].widget.attrs['placeholder'] = (
            "Your organization's name as you'd like it to appear on our website."
        )
        self.fields['membership_level'].help_text = (
            'See <a href="/foundation/corporate-membership/#dues">dues</a> for '
            'details on the levels.'
        )
        self.fields['address'].widget.attrs['placeholder'] = (
            'Mailing address'
        )
        self.fields['address'].help_text = (
            'We can send the invoice by email, but we need a contact address.'
        )
        self.fields['description'].widget.attrs['placeholder'] = (
            "A short paragraph that describes your organization and its "
            "activities, written as if the DSF were describing your company "
            "to a third party."
        )
        self.fields['description'].help_text = (
            """We'll use this text on the <a href="/foundation/corporate-members/">
            corporate membership page</a>; you can use the existing descriptions
            as a guide for flavor we're looking for."""
        )

    class Meta:
        fields = [
            'display_name',
            'billing_name',
            'logo',
            'url',
            'contact_name',
            'contact_email',
            'billing_email',
            'membership_level',
            'address',
            'description',
        ]
        model = CorporateMember
