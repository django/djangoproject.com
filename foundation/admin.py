from django.contrib import admin
from django.utils.text import slugify
from django.utils.translation import gettext as _

from . import models


@admin.register(models.Office)
class OfficeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "office", "term")
    list_filter = ("office", "term")
    list_select_related = True
    raw_id_fields = ("account",)

    @admin.display(ordering="account__last_name")
    def full_name(self, obj):
        return obj.account.get_full_name()


@admin.register(models.NonBoardAttendee)
class NonBoardAttendeeAdmin(admin.ModelAdmin):
    pass


class GrantInline(admin.TabularInline):
    model = models.ApprovedGrant


class IndividualMemberInline(admin.TabularInline):
    model = models.ApprovedIndividualMember


class CorporateMemberInline(admin.TabularInline):
    model = models.ApprovedCorporateMember


class BusinessInline(admin.StackedInline):
    model = models.Business


class ActionItemInline(admin.StackedInline):
    model = models.ActionItem


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "created_at", "updated_at"]
    list_editable = ["is_active"]
    readonly_fields = ["created_by", "created_at", "updated_by", "updated_at"]
    fieldsets = [
        (None, {"fields": ["title", "body", "is_active"]}),
        (
            "Call to action",
            {
                "description": (
                    "Both fields should be defined for the CTA button to be displayed."
                ),
                "fields": ["cta_label", "cta_url"],
            },
        ),
        (
            "Metadata",
            {"fields": ["created_by", "created_at", "updated_by", "updated_at"]},
        ),
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.Meeting)
class MeetingAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Metadata",
            {
                "fields": (
                    "title",
                    "slug",
                    "date",
                    "leader",
                    "board_attendees",
                    "non_board_attendees",
                ),
            },
        ),
        (
            "Treasurer report",
            {
                "fields": ("treasurer_balance", "treasurer_report"),
            },
        ),
    )
    filter_horizontal = ("board_attendees", "non_board_attendees")
    inlines = [
        GrantInline,
        IndividualMemberInline,
        CorporateMemberInline,
        BusinessInline,
        ActionItemInline,
    ]
    list_display = ("title", "date")
    list_filter = ("date",)
    prepopulated_fields = {"slug": ("title",)}

    def get_changeform_initial_data(self, request):
        title = _("DSF Board monthly meeting")
        return {
            "title": title,
            "slug": slugify(title),
        }


class CoreAwardAdmin(admin.ModelAdmin):
    list_display = ["recipient", "cohort"]


admin.site.register(models.CoreAward, CoreAwardAdmin)
admin.site.register(models.CoreAwardCohort)
