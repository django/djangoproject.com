from django.conf import settings
from django.core import mail
from django.test import TestCase

from .forms import CorporateMemberSignUpForm
from .utils import get_temporary_image


class CorporateMemberCorporateMemberSignUpFormTests(TestCase):

    def setUp(self):
        test_image = get_temporary_image()
        self.valid_data = {
            'display_name': 'Foo Widgets',
            'billing_name': 'Foo Widgets, Inc.',
            'url': 'http://example.com',
            'contact_name': 'Joe Developer',
            'contact_email': 'joe@example.com',
            'billing_email': '',
            'membership_level': 2,
            'address': 'USA',
            'description': 'We make widgets!',
            'amount': 2000,
        }
        self.file_data = {'logo': test_image}

    def test_submit_success(self):
        data = self.valid_data
        form = CorporateMemberSignUpForm(data, self.file_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.display_name, data['display_name'])
        self.assertEqual(instance.invoice_set.get().amount, data['amount'])

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Django Corporate Membership Application: Foo Widgets')
        self.assertEqual(msg.body, (
            "Thanks for applying to be a corporate member of the Django Software Foundation! "
            "Your application is received and we'll follow up with an invoice soon."
        ))
        self.assertEqual(msg.from_email, settings.FUNDRAISING_DEFAULT_FROM_EMAIL)
        self.assertEqual(
            msg.to,
            [settings.FUNDRAISING_DEFAULT_FROM_EMAIL, data['contact_email'], 'treasurer@djangoproject.com']
        )

    def test_logo_required(self):
        form = CorporateMemberSignUpForm(self.valid_data)  # missing request.FILES
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'logo': ['This field is required.']})
