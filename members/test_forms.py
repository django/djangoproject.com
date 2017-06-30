from django.conf import settings
from django.core import mail
from django.test import TestCase

from .forms import CorporateMemberSignUpForm
from .models import CorporateMember
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
            'django_usage': 'fun',
            'amount': 2000,
        }
        self.file_data = {'logo': test_image}

    def test_submit_success(self):
        data = self.valid_data
        form = CorporateMemberSignUpForm(data, self.file_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.display_name, data['display_name'])
        self.assertEqual(instance.django_usage, 'fun')
        self.assertEqual(instance.invoice_set.get().amount, data['amount'])

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Django Corporate Membership Application: Foo Widgets')
        self.assertEqual(msg.body, (
            "Thanks for applying to be a corporate member of the Django Software Foundation! "
            "Your application is being reviewed, and we'll follow up a "
            "response from the board after our next monthly meeting."
        ))
        self.assertEqual(msg.from_email, settings.FUNDRAISING_DEFAULT_FROM_EMAIL)
        self.assertEqual(
            msg.to,
            [
                settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
                data['contact_email'],
                'treasurer@djangoproject.com',
                'dsf-board@googlegroups.com',
            ]
        )

    def test_logo_required(self):
        form = CorporateMemberSignUpForm(self.valid_data)  # missing request.FILES
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'logo': ['This field is required.']})

    def test_django_usage_required(self):
        data = self.valid_data.copy()
        del data['django_usage']
        form = CorporateMemberSignUpForm(data, self.file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'django_usage': ['This field is required.']})

    def test_renewal_success(self):
        model_data = self.valid_data.copy()
        del model_data['amount']
        member = CorporateMember.objects.create(**model_data)
        data = self.valid_data
        form = CorporateMemberSignUpForm(data, self.file_data, instance=member)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.display_name, data['display_name'])
        self.assertEqual(instance.django_usage, 'fun')
        self.assertEqual(instance.invoice_set.get().amount, data['amount'])

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Django Corporate Membership Renewal: Foo Widgets')
        self.assertEqual(msg.body, (
            "Thanks for renewing as a corporate member of the Django Software Foundation! "
            "Your renewal is received, and we'll follow up with an invoice soon."
        ))
        self.assertEqual(msg.from_email, settings.FUNDRAISING_DEFAULT_FROM_EMAIL)
        self.assertEqual(
            msg.to,
            [
                settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
                data['contact_email'],
                'treasurer@djangoproject.com',
                'dsf-board@googlegroups.com',
            ]
        )
