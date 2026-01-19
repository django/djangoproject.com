from django import forms
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponse
from django.utils.html import format_html

from releases.models import Release

from .models import (
    BugFixRelease,
    FeatureRelease,
    PreRelease,
    Releaser,
    SecurityIssue,
    SecurityIssueReleasesThrough,
    SecurityRelease,
)


@admin.register(Releaser)
class ReleaserAdmin(admin.ModelAdmin):
    list_display = ["user", "key_id", "key_url"]


class ReleaseChecklistAdminMixin:
    list_display = ["version", "when", "releaser", "checklist_link"]
    list_filter = ["releaser"]
    actions = ["render_checklist"]
    readonly_fields = ["blogpost_link"]

    def queryset(self, request):
        return super().get_queryset(request).select_related("release")

    @admin.action(description="Render checklists for selected releases")
    def render_checklist(self, request, queryset):
        errors = []
        try:
            instance = queryset.get()
        except (Release.DoesNotExist, Release.MultipleObjectsReturned):
            errors.append("A single item should be selected")
            instance = None

        if (
            isinstance(instance, SecurityRelease)
            and not instance.securityissue_set.filter(releases__isnull=False).exists()
        ):
            errors.append("Please provide at least one SecurityIssueReleasesThrough.")

        if errors:
            for error in errors:
                self.message_user(request, error, messages.ERROR)
            return

        checklist = instance.render_to_string(request=request)
        return HttpResponse(checklist, content_type="text/markdown; charset=utf-8")

    @admin.display(description="Checklist")
    def checklist_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank">View checklist</a>', url)


@admin.register(BugFixRelease)
class BugFixReleaseAdmin(ReleaseChecklistAdminMixin, admin.ModelAdmin):
    pass


@admin.register(PreRelease)
class PreReleaseAdmin(ReleaseChecklistAdminMixin, admin.ModelAdmin):
    list_display = ["feature_release"] + ReleaseChecklistAdminMixin.list_display
    list_filter = ["feature_release"] + ReleaseChecklistAdminMixin.list_filter


@admin.register(FeatureRelease)
class FeatureReleaseAdmin(ReleaseChecklistAdminMixin, admin.ModelAdmin):
    list_display = ReleaseChecklistAdminMixin.list_display + ["tagline"]


@admin.register(SecurityRelease)
class SecurityReleaseAdmin(ReleaseChecklistAdminMixin, admin.ModelAdmin):
    list_display = ["versions", "cves", "when", "releaser", "checklist_link"]
    search_fields = ["affected_branches"]
    ordering = ["-when"]
    readonly_fields = ["hashes_by_versions"]


class SecurityIssueReleasesThroughInline(admin.TabularInline):
    model = SecurityIssueReleasesThrough
    extra = 0
    autocomplete_fields = ["release"]


@admin.register(SecurityIssue)
class SecurityIssueAdmin(admin.ModelAdmin):
    list_display = [
        "cve_year_number",
        "summary",
        "severity",
        "commit_hash_main",
        "cve_json_record_link",
    ]
    list_filter = ["severity", "release"]
    search_fields = ["cve_year_number", "summary", "description", "commit_hash_main"]
    ordering = ["-updated_at", "-created_at", "-cve_year_number"]
    readonly_fields = [
        "cvss_base_severity",
        "cvss_vector",
    ]
    inlines = [SecurityIssueReleasesThroughInline]
    formfield_overrides = {
        models.CharField: {"widget": forms.TextInput(attrs={"size": "100"})},
    }

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "cna",
                    "cve_year_number",
                    "severity",
                    "summary",
                    "description",
                    "blogdescription",
                    "reporter",
                    "remediator",
                    "reported_at",
                    "confirmed_at",
                    "cve_type",
                    "impact",
                    "release",
                    "commit_hash_main",
                )
            },
        ),
        (
            "CVSS 4.0 Fields - Base Metrics - Exploitability",
            {
                "fields": (
                    "attack_vector",
                    "attack_complexity",
                    "attack_requirements",
                    "privileges_required",
                    "user_interaction",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "CVSS 4.0 Fields - Base Metrics - Vulnerable System Impact",
            {
                "fields": (
                    "vuln_confidentiality_impact",
                    "sub_confidentiality_impact",
                    "vuln_integrity_impact",
                    "sub_integrity_impact",
                    "vuln_availability_impact",
                    "sub_availability_impact",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "CVSS 4.0 Fields - Supplemental Metrics",
            {
                "fields": (
                    "safety",
                    "automatable",
                    "recovery",
                    "value_density",
                    "vulnerability_response_effort",
                    "provider_urgency",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "CVSS 4.0 Fields - Score and Vector",
            {
                "fields": (
                    "cvss_base_score",
                    "cvss_base_severity",
                    "cvss_vector",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "Deprecated",
            {
                "fields": (
                    "other_type",
                    "attack_type",
                ),
                "classes": ["collapse"],
            },
        ),
    )

    @admin.display(description="CVE Record")
    def cve_json_record_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank">CVE Record</a>', url)


@admin.register(SecurityIssueReleasesThrough)
class SecurityIssueReleasesThroughAdmin(admin.ModelAdmin):
    list_display = ["securityissue__cve_year_number", "release__version", "commit_hash"]
    list_filter = ["securityissue__cve_year_number", "release__version"]
    search_fields = [
        "securityissue__cve_year_number",
        "release__version",
        "commit_hash",
    ]
    ordering = ["-securityissue__cve_year_number", "release__version"]
