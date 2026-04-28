from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import (
    BugFixRelease,
    FeatureRelease,
    PreRelease,
    Releaser,
    SecurityIssue,
    SecurityIssueReleasesThrough,
    SecurityRelease,
    cve_sort_key,
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
    readonly_fields = [
        "cvss_v3_severity",
        "cvss_v4_severity",
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
            "CVSS Scores",
            {
                "description": (
                    "<p>Use an approved calculator to get the vector string and score, "
                    "then enter both here. Calculators: "
                    '<a href="https://www.first.org/cvss/calculator/3.1">CVSS v3.1</a> '
                    '<a href="https://www.first.org/cvss/calculator/4.0">CVSS v4.0</a> '
                    "</p>"
                ),
                "fields": (
                    "cvss_v3_vector_string",
                    "cvss_v3_score",
                    "cvss_v3_severity",
                    "cvss_v4_vector_string",
                    "cvss_v4_score",
                    "cvss_v4_severity",
                ),
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

    def get_ordering(self, request):
        return [
            "-updated_at",
            "-created_at",
            *cve_sort_key(desc=True),
        ]

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

    def get_ordering(self, request):
        return [
            *cve_sort_key("securityissue__cve_year_number", desc=True),
            "release__version",
        ]
