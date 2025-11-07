from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import IndividualMember

User = get_user_model()


class IndividualMemberTests(TestCase):
    def test_migration_members_0012_link_individual_members_to_users_by_email(self):
        stdout = StringIO()
        stderr = StringIO()

        call_command(
            "migrate",
            "members",
            "0011",
            no_input=True,
            stdout=stdout,
            stderr=stderr,
        )

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

        call_command(
            "migrate",
            "members",
            "0012",
            no_input=True,
            stdout=stdout,
            stderr=stderr,
        )

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
