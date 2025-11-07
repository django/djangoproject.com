from datetime import date, timedelta
from io import StringIO

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils.formats import localize

from members.models import (
    SILVER_MEMBERSHIP,
    CorporateMember,
    IndividualMember,
    IndividualMemberAccountInviteSendMailStatus,
)


class IndividualMemberTests(TestCase):
    def test_send_individual_member_account_invite_mails(self):
        IndividualMember.objects.create(
            name="Member 1",
            email="member1@example.com",
        )
        IndividualMember.objects.create(
            name="Member 2",
            email="member2@example.com",
            member_until=date.today() - timedelta(days=7),
        )
        stdout = StringIO()
        stderr = StringIO()
        call_command(
            "send_individual_member_account_invite_mails",
            stdout=stdout,
            stderr=stderr,
        )
        self.assertEqual(len(mail.outbox), 1)
        stdout_output = stdout.getvalue()
        stderr_output = stderr.getvalue()
        self.assertGreater(len(stdout_output), 0)
        self.assertEqual(len(stderr_output), 0)
        stdout_output_lines = stdout_output.splitlines()
        self.assertIn(
            f"{IndividualMemberAccountInviteSendMailStatus.SENT}: 1",
            stdout_output_lines,
        )

    def test_send_individual_member_account_invite_mails_including_former_members(self):
        IndividualMember.objects.create(
            name="Member 1",
            email="member1@example.com",
        )
        IndividualMember.objects.create(
            name="Member 2",
            email="member2@example.com",
            member_until=date.today() - timedelta(days=7),
        )
        call_command(
            "send_individual_member_account_invite_mails",
            "--include-former-members",
            "--no-logging",
        )
        self.assertEqual(len(mail.outbox), 2)


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
