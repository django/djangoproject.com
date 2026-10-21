from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import IndividualMember, IndividualMemberAccountInviteSendMailStatus


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--include-former-members",
            action="store_true",
            help="Include former members to the queryset.",
        )

        parser.add_argument(
            "--no-logging",
            action="store_true",
            help="Disable writing results to stdout/stderr.",
        )

    def handle(self, *args, **options):
        queryset = IndividualMember.objects.filter(
            user_id__isnull=True,
            account_invite_mail_sent_at__isnull=True,
        )
        if not options["include_former_members"]:
            queryset = queryset.filter(member_until__isnull=True)
        with transaction.atomic():
            results = IndividualMember.send_account_invite_mails(queryset)
        if not options["no_logging"]:
            self.write_account_invite_send_mail_results(results)

    def write_account_invite_send_mail_results(self, results):
        for (
            status_enum_member,
            status_enum_value,
        ) in IndividualMemberAccountInviteSendMailStatus.__members__.items():
            count = results.get(status_enum_value, 0)
            writer = self.stdout
            if (
                status_enum_value == IndividualMemberAccountInviteSendMailStatus.FAILED
                and count > 0
            ):  # pragma: no cover
                writer = self.stderr
            writer.write(f"{status_enum_member}: {count}")
