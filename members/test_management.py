from datetime import date, timedelta
from io import StringIO
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils.formats import localize

from members.management.commands.import_demo_corporate_members import (
    Command as ImportCommand,
)
from members.models import PLATINUM_MEMBERSHIP, SILVER_MEMBERSHIP, CorporateMember


class CorporateMemberTests(TestCase):
    today = date.today()
    twenty_nine_days_from_now = today + timedelta(days=29)
    thirty_days_from_now = today + timedelta(days=30)

    @classmethod
    def setUpTestData(cls):
        cls.member = CorporateMember.objects.create(
            display_name="Corporation",
            billing_name="foo",
            billing_email="billing@example.com",
            contact_email="contact@example.com",
            contact_name="Contact Name",
            membership_level=SILVER_MEMBERSHIP,
        )

    def test_no_email(self):
        self.member.invoice_set.create(
            amount=0, expiration_date=self.twenty_nine_days_from_now
        )
        call_command("send_renewal_emails")
        self.assertEqual(len(mail.outbox), 0)

    def test_mail(self):
        self.member.invoice_set.create(
            amount=0, expiration_date=self.thirty_days_from_now
        )
        call_command("send_renewal_emails")
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox.pop()
        self.assertEqual(
            msg.subject,
            "Expiring Django Software Foundation Membership for Corporation",
        )
        self.assertIn("Hi Contact Name,", msg.body)
        self.assertIn(
            "The Django Software Foundation membership for Corporation expires\n"
            "%s. Would you like to renew your support?"
            % localize(self.thirty_days_from_now),
            msg.body,
        )
        self.assertIn(
            "http://www.djangoproject.localhost:8000/foundation/"
            "corporate-membership/renew/",
            msg.body,
        )
        self.assertEqual(msg.from_email, settings.FUNDRAISING_DEFAULT_FROM_EMAIL)
        self.assertEqual(
            msg.to,
            [
                settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
                "contact@example.com",
            ],
        )


SAMPLE_HTML = """
<h3>Platinum Corporate Members ($30,000+)</h3>
<ul class="corporate-members">
<li>
  <img src="https://media.example.com/logo.png" alt="Acme" class="corporate-member-logo" />
  <h3><a href="https://acme.example.com/">Acme</a></h3>
  <p>On top.<br>Second line.</p>
</li>
<li>
  <img src="https://media.example.com/other.jpg" alt="Widgets R Us" class="corporate-member-logo" />
  <h3><a href="https://widgets.example.com/">Widgets R Us</a></h3>
  <p>Makes widgets.</p>
</li>
</ul>
"""


class ImportDemoCorporateMembersTests(TestCase):
    def test_parse_tiers_members_and_descriptions(self):
        entries = ImportCommand().parse(SAMPLE_HTML)

        self.assertEqual(len(entries), 2)
        first = entries[0]
        self.assertEqual(first["name"], "Acme")
        self.assertEqual(first["url"], "https://acme.example.com/")
        self.assertEqual(first["description"], "On top. Second line.")
        self.assertEqual(first["logo"], "https://media.example.com/logo.png")
        self.assertEqual(first["level"], PLATINUM_MEMBERSHIP)

    @patch("members.management.commands.import_demo_corporate_members.requests.get")
    def test_handle_creates_members_and_logos(self, mock_get):
        def fake_get(url, *args, **kwargs):
            response = MagicMock()
            if "corporate-members" in url:
                response.text = SAMPLE_HTML
            else:
                response.content = b"fake-image-bytes"
            response.raise_for_status.return_value = None
            return response

        mock_get.side_effect = fake_get

        call_command("import_demo_corporate_members", stdout=StringIO(), verbosity=0)

        member = CorporateMember.objects.get(display_name="Acme")
        self.assertEqual(member.membership_level, PLATINUM_MEMBERSHIP)
        self.assertEqual(member.url, "https://acme.example.com/")
        self.assertTrue(member.logo)
        self.assertTrue(member.invoice_set.exists())
        self.assertEqual(CorporateMember.objects.count(), 2)

    @patch("members.management.commands.import_demo_corporate_members.requests.get")
    def test_handle_is_idempotent(self, mock_get):
        def fake_get(url, *args, **kwargs):
            response = MagicMock()
            if "corporate-members" in url:
                response.text = SAMPLE_HTML
            else:
                response.content = b"fake-image-bytes"
            response.raise_for_status.return_value = None
            return response

        mock_get.side_effect = fake_get

        call_command("import_demo_corporate_members", stdout=StringIO(), verbosity=0)
        call_command("import_demo_corporate_members", stdout=StringIO(), verbosity=0)

        self.assertEqual(CorporateMember.objects.count(), 2)
        self.assertEqual(
            CorporateMember.objects.get(display_name="Acme").invoice_set.count(), 1
        )
