from contextlib import ExitStack
from datetime import date, timedelta
from threading import Event, Thread

from django.contrib.auth import get_user_model
from django.core import mail
from django.db import DatabaseError, connections, transaction
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from members.models import (
    GOLD_MEMBERSHIP,
    PLATINUM_MEMBERSHIP,
    SILVER_MEMBERSHIP,
    CorporateMember,
    IndividualMember,
    IndividualMemberAccountInviteSendMailStatus,
    Team,
)

User = get_user_model()


class IndividualMemberTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = IndividualMember.objects.create(
            name="DjangoDeveloper", email="developer@example.com"
        )

    def setUp(self):
        self.member.refresh_from_db()

    def test_str(self):
        self.assertEqual(str(self.member), "DjangoDeveloper")

    def test_member_since_should_have_default(self):
        self.assertEqual(IndividualMember().member_since, date.today())

    def test_is_active(self):
        self.assertTrue(self.member.is_active)
        self.member.member_until = date.today()
        self.assertFalse(self.member.is_active)

    def test_match_and_set_users_by_email(self):
        members_count = 4
        user_pk_to_email_mapping = {}
        for i in range(members_count):
            username = f"user{i}"
            email = f"{username}@example.com"
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password",
            )
            user_pk_to_email_mapping[user.pk] = email
            IndividualMember.objects.create(
                name=f"User {i}",
                email=email,
            )
        self.assertEqual(
            IndividualMember.objects.filter(
                user_id__isnull=True,
                email__in=user_pk_to_email_mapping.values(),
            ).count(),
            members_count,
        )
        IndividualMember.match_and_set_users_by_email()
        individual_member_queryset = IndividualMember.objects.filter(
            user_id__in=user_pk_to_email_mapping.keys(),
        )
        self.assertEqual(
            individual_member_queryset.count(),
            members_count,
        )
        for individual_member in individual_member_queryset.iterator():
            self.assertEqual(
                individual_member.email,
                user_pk_to_email_mapping[individual_member.user_id],
            )

    def test_send_account_invite_mails(self):
        individual_members_count = 2
        individual_member_pks = set()
        for i in range(individual_members_count):
            username = f"user{i}"
            email = f"{username}@example.com"
            individual_member = IndividualMember.objects.create(
                name=f"User {i}",
                email=email,
            )
            individual_member_pks.add(individual_member.pk)
        self.assertEqual(len(mail.outbox), 0)
        results = IndividualMember.send_account_invite_mails(
            IndividualMember.objects.filter(
                pk__in=individual_member_pks,
            )
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            next(iter(results.keys())),
            IndividualMemberAccountInviteSendMailStatus.SENT,
        )
        self.assertEqual(
            results[IndividualMemberAccountInviteSendMailStatus.SENT],
            individual_members_count,
        )
        self.assertEqual(len(mail.outbox), individual_members_count)

    def test_send_account_invite_mail(self):
        individual_member = IndividualMember.objects.create(
            name="Member 1",
            email="member1@example.com",
        )
        self.assertEqual(len(mail.outbox), 0)
        status = individual_member.send_account_invite_mail()
        self.assertEqual(
            status,
            IndividualMemberAccountInviteSendMailStatus.SENT,
        )
        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox.pop()
        self.assertIn(individual_member.email, email_message.to)
        self.assertEqual(
            email_message.subject,
            "Django Individual Membership - Account Setup",
        )
        self.assertIn(f"Hello {individual_member.name},", email_message.body)
        self.assertIn(reverse("registration_register"), email_message.body)


class IndividualMemberTransactionTests(TransactionTestCase):
    def test_send_account_invite_mails_prevents_race_condition(self):
        new_individual_members_count = 2

        # Strictly required for the test.
        self.assertGreaterEqual(new_individual_members_count, 1)

        individual_member_pks = set()
        for i in range(new_individual_members_count):
            individual_member = IndividualMember.objects.create(
                name=f"User {i}",
                email=f"user{i}@example.com",
            )
            individual_member_pks.add(individual_member.pk)

        individual_members_queryset = IndividualMember.objects.filter(
            pk__in=individual_member_pks,
        )

        lock_signal = Event()
        unlock_request_signal = Event()

        def lock_individual_members():
            # This is a thread entry point. Note that Django doesn't close
            # our custom connections created in separated threads, which
            # causes `django.db.utils.OperationalError` to be raised with
            # message "There are N other sessions using the database" in most
            # cases.
            #
            # Ensure all the connections are closed at the end.
            with ExitStack() as exit_stack:
                exit_stack.callback(connections.close_all)
                with transaction.atomic():
                    locked_individual_members_queryset = individual_members_queryset.select_for_update()
                    # Trigger the fetch operation.
                    self.assertEqual(len(locked_individual_members_queryset), new_individual_members_count)
                    lock_signal.set()
                    unlock_request_signal.wait()

        caught_exception = None

        with transaction.atomic():
            locker_thread = Thread(target=lock_individual_members)
            locker_thread.start()

            self.assertTrue(lock_signal.wait(timeout=10))

            with ExitStack() as exit_stack:
                exit_stack.callback(unlock_request_signal.set)

                with self.assertRaises(DatabaseError) as exception_cm:
                    IndividualMember.send_account_invite_mails(
                        individual_members_queryset,
                        select_for_update_nowait=True,
                    )

                caught_exception = exception_cm.exception

        locker_thread.join(timeout=10)

        self.assertIsNotNone(caught_exception)
        self.assertIn("could not obtain lock on row in relation", str(caught_exception))

        self.assertEqual(
            individual_members_queryset.filter(
                account_invite_mail_sent_at__isnull=True,
            ).count(),
            new_individual_members_count,
        )


class CorporateMemberTests(TestCase):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    @classmethod
    def setUpTestData(cls):
        cls.member = CorporateMember.objects.create(
            display_name="Corporation",
            billing_name="foo",
            billing_email="c@example.com",
            contact_email="c@example.com",
            membership_level=SILVER_MEMBERSHIP,
        )

    def setUp(self):
        self.member.refresh_from_db()

    def test_str(self):
        self.assertEqual(str(self.member), "Corporation")

    def test_is_invoiced(self):
        # No invoices == not invoiced.
        self.assertEqual(self.member.is_invoiced, False)
        # Invoice but no sent_date == not invoiced.
        invoice = self.member.invoice_set.create(amount=500)
        self.assertEqual(self.member.is_invoiced, False)
        # Invoice with an sent_date == invoiced.
        invoice.sent_date = self.today
        invoice.save()
        self.assertEqual(self.member.is_invoiced, True)

    def test_is_paid(self):
        # No invoices == not paid.
        self.assertEqual(self.member.is_paid, False)
        # Invoice but no paid_date == not paid.
        invoice = self.member.invoice_set.create(amount=500)
        self.assertEqual(self.member.is_paid, False)
        # Invoice with a paid_date == paid.
        invoice.paid_date = self.today
        invoice.save()
        self.assertEqual(self.member.is_paid, True)

    def test_get_expiry_date(self):
        self.assertIsNone(self.member.get_expiry_date())
        self.member.invoice_set.create(amount=500)
        self.assertIsNone(self.member.get_expiry_date())
        self.member.invoice_set.create(amount=500, expiration_date=self.today)
        self.assertEqual(self.member.get_expiry_date(), self.today)
        self.member.invoice_set.create(amount=500, expiration_date=self.tomorrow)
        self.assertEqual(self.member.get_expiry_date(), self.tomorrow)

    def test_manager_by_membership_level(self):
        self.assertEqual(CorporateMember.objects.by_membership_level(), {})
        self.member.invoice_set.create(amount=500, expiration_date=self.tomorrow)
        self.assertEqual(
            CorporateMember.objects.by_membership_level(), {"silver": [self.member]}
        )
        self.member.membership_level = GOLD_MEMBERSHIP
        self.member.save()
        self.assertEqual(
            CorporateMember.objects.by_membership_level(), {"gold": [self.member]}
        )
        self.member.membership_level = PLATINUM_MEMBERSHIP
        self.member.save()
        self.assertEqual(
            CorporateMember.objects.by_membership_level(), {"platinum": [self.member]}
        )


class TeamTests(TestCase):
    def test_str(self):
        self.assertEqual(str(Team(name="Ops")), "Ops")
