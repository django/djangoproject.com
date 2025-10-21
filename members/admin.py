from datetime import date, timedelta

from django.contrib import admin, messages
from django.contrib.auth import get_permission_codename
from django.db import transaction
from django.templatetags.static import static
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _, ngettext

from members.models import (
    CorporateMember,
    IndividualMember,
    IndividualMemberAccountInviteSendMailStatus,
    Invoice,
    Team,
)


@admin.register(IndividualMember)
class IndividualMemberAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "is_active",
        "member_since",
        "member_until",
        "account_invite_mail_sent_at",
    ]
    search_fields = ["name"]
    list_filter = ["member_until", "account_invite_mail_sent_at"]
    autocomplete_fields = ["user"]
    actions = ["send_account_invite_mail"]

    @admin.action(
        description=_("Send account invite mail to selected individual members"),
        permissions=["send_account_invite_mail"],
    )
    def send_account_invite_mail(self, request, queryset):
        with transaction.atomic():
            results = IndividualMember.send_account_invite_mails(queryset)
        sent_count = results.get(
            IndividualMemberAccountInviteSendMailStatus.SENT,
            0,
        )
        failed_count = results.get(
            IndividualMemberAccountInviteSendMailStatus.FAILED,
            0,
        )
        skipped_count = results.get(
            IndividualMemberAccountInviteSendMailStatus.SKIPPED,
            0,
        )
        if sent_count > 0:
            self.message_user(
                request,
                ngettext(
                    "Sent account invite mail to 1 individual member.",
                    "Sent account invite mail to %(count)d individual members.",
                    sent_count,
                )
                % {"count": sent_count},
                messages.SUCCESS,
            )
        if failed_count > 0:
            self.message_user(
                request,
                ngettext(
                    "Failed to send account invite mail to 1 individual member.",
                    "Failed to send account invite mail to %(count)d individual members.",
                    failed_count,
                )
                % {"count": failed_count},
                messages.ERROR,
            )
        if skipped_count > 0:
            self.message_user(
                request,
                ngettext(
                    "Skipped sending account invite mail to 1 individual member (already has an account linked or an invite mail has been sent).",
                    "Skipped sending account invite mail to %(count)d individual members (already have accounts linked or invite mails have been sent).",
                    skipped_count,
                )
                % {"count": skipped_count},
                messages.INFO,
            )

    def has_send_account_invite_mail_permission(self, request):
        codename = get_permission_codename("send_account_invite_mail", self.opts)
        return request.user.has_perm("%s.%s" % (self.opts.app_label, codename))


class InvoiceInline(admin.TabularInline):
    model = Invoice


class StatusFilter(admin.SimpleListFilter):
    """
    Display only active members in the changelist page, by default.
    """

    title = _("Status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            (None, _("Active")),
            ("inactive", _("Inactive")),
            ("all", _("All")),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string({self.parameter_name: lookup}, []),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(inactive=False)
        elif self.value() == "inactive":
            return queryset.filter(inactive=True)
        else:
            return queryset


@admin.register(CorporateMember)
class CorporateMemberAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "membership_expires",
        "_is_invoiced",
        "_is_paid",
        "contact_email",
        "membership_level",
        "renewal_link",
    ]
    list_filter = [StatusFilter, "membership_level"]
    inlines = [InvoiceInline]
    search_fields = ["display_name", "billing_name"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("invoice_set")

    def renewal_link(self, obj):
        return format_html(
            '<a href="{}"><img src="{}" alt="{}" />',
            obj.get_renewal_link(),
            static("admin/img/icon-changelink.svg"),
            _("renewal link"),
        )

    def membership_expires(self, obj):
        expiry_date = obj.get_expiry_date()
        if expiry_date:
            today = date.today()
            # Expired.
            if expiry_date < today:
                color = "red"
            # Expires within 30 days.
            elif expiry_date < today + timedelta(days=30):
                color = "orange"
            # Expires more than 30 days from today.
            else:
                color = "green"
            expiry_date = format_html(
                '<span style="color: {}">{}</span>',
                color,
                localize(expiry_date),
            )
        return expiry_date


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ["members"]
    prepopulated_fields = {"slug": ("name",)}
