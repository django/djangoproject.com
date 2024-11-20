from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from .models import CorporateMember


class CorporateMemberSignUpForm(forms.ModelForm):
    amount = forms.IntegerField(
        label=_("Donation amount"),
        help_text=_("Enter an integer in US$ without the dollar sign."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkbox_fields = []
        self.radio_select_fields = []
        self.label_fields = []
        self.fields["logo"].required = True
        self.fields["django_usage"].required = True
        for name, field in self.fields.items():
            help_text = field.help_text
            if help_text:
                help_text = " (" + help_text + ")"
                self.fields[name].help_text = ""
            self.fields[name].widget.attrs = {"placeholder": field.label + help_text}

            if isinstance(field.widget, forms.CheckboxInput):
                self.checkbox_fields.append(name)
            elif isinstance(field.widget, forms.RadioSelect):
                self.radio_select_fields.append(name)
            elif isinstance(field.widget, (forms.FileInput, forms.Select)):
                self.label_fields.append(name)

        self.fields["billing_name"].widget.attrs["placeholder"] = _(
            "Billing name (If different from above name)."
        )
        self.fields["billing_name"].help_text = _(
            "For example, this might be your full registered company name."
        )
        self.fields["display_name"].widget.attrs["placeholder"] = _(
            "Your organization's name as you'd like it to appear on our website."
        )
        self.fields["address"].widget.attrs["placeholder"] = _("Mailing address")
        self.fields["address"].help_text = _(
            "We can send the invoice by email, but we need a contact address."
        )
        self.fields["description"].widget.attrs["placeholder"] = _(
            "A short paragraph that describes your organization and its "
            "activities, written as if the DSF were describing your company "
            "to a third party."
        )
        self.fields["description"].help_text = _(
            """We'll use this text on the
            <a href="/foundation/corporate-members/">
            corporate membership page</a>; you can use the existing descriptions
            as a guide for flavor we're looking for."""
        )
        self.fields["django_usage"].widget.attrs["placeholder"] = _(
            "How does your organization use Django?"
        )
        self.fields["django_usage"].help_text = _(
            "This won't be displayed publicly but helps the DSF Board "
            "to evaluate your application."
        )
        self.fields["amount"].help_text = _(
            """Enter an amount above and the appropriate membership level will
            be automatically selected. Or select a membership level below and
            the minimum donation will be entered for you. See
            <a href="/foundation/corporate-membership/#dues">dues</a> for
            details on the levels."""
        )

    class Meta:
        fields = [
            "display_name",
            "billing_name",
            "logo",
            "url",
            "contact_name",
            "contact_email",
            "billing_email",
            "address",
            "description",
            "django_usage",
            "amount",
            "membership_level",
        ]
        model = CorporateMember

    @property
    def is_renewing(self):
        return not self.instance._state.adding

    def save(self, *args, **kwargs):
        is_renewing = self.is_renewing  # self.is_renewing changes after super()
        instance = super().save(*args, **kwargs)
        display_name = self.instance.display_name
        if is_renewing:
            subject = _("Django Corporate Membership Renewal: %s") % display_name
            content = _(
                "Thanks for renewing as a corporate member of the "
                "Django Software Foundation! "
                "Your renewal is received, and we'll follow up with an invoice soon."
            )
        else:
            subject = _("Django Corporate Membership Application: %s") % display_name
            content = _(
                "Thanks for applying to be a corporate member of the "
                "Django Software Foundation! "
                "Your application is being reviewed, and we'll follow up a "
                "response from the board after our next monthly meeting."
            )
        send_mail(
            subject,
            content,
            settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
            [
                settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
                self.instance.contact_email,
                "treasurer@djangoproject.com",
                "dsf-board@googlegroups.com",
            ],
        )
        instance.invoice_set.create(amount=self.cleaned_data["amount"])
        return instance
