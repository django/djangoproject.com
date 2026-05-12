import datetime
import json

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Cast, Substr
from django.shortcuts import reverse
from django.template.defaultfilters import urlize
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property

from releases.models import Release

from .templatetags.checklist_extras import enumerate_items, format_releases_for_cves

CNA_DSF_UUID = "6a34fbeb-21d4-45e7-8e0a-62b95bc12c92"


# CVE IDs have the form CVE-YYYY-NNNNN. The year (4 digits) is always at
# positions 5-8 and the number starts at position 10 (both 1-based). This
# helper extracts each part as an integer for correct numeric DB-level sorting.
def cve_sort_key(field="cve_year_number", *, desc=False):
    year = Cast(Substr(field, 5, 4), output_field=models.IntegerField())
    number = Cast(Substr(field, 10), output_field=models.IntegerField())
    if desc:
        return year.desc(), number.desc()
    return year, number


DESCRIPTION_HELP_TEXT = """Written in present tense.

Used in CVE metadata. Single `backticks` for inline code.

==> Do not include versions, these will be prepended automatically. <==

CVE documented format suggestions:

<pre>
    •[VULNTYPE] in [COMPONENT] in [VENDOR] [PRODUCT] [VERSION] allows
    [ATTACKER] to [IMPACT] via [VECTOR].

    •[COMPONENT] in [VENDOR] [PRODUCT] [VERSION] [ROOT CAUSE], which allows
    [ATTACKER] to [IMPACT] via [VECTOR]
</pre>

Examples:
<pre>
    The password hasher in contrib/auth/hashers.py allows remote attackers to
    enumerate users via a timing attack involving login requests.

    The `intcomma` template filter is subject to a potential denial-of-service
    attack when used with very long strings.

    The `django.contrib.auth.forms.UsernameField` is subject to a potential
    denial-of-service attack via certain inputs with a very large number of
    Unicode characters (because the NFKC normalization is slow on Windows).
</pre>
"""
SEVERITY_LEVELS_DOCS = (
    "https://docs.djangoproject.com/en/dev/internals/security/"
    "#security-issue-severity-levels"
)


def get_cve_default():
    return f"CVE-{datetime.date.today().year}-{get_random_string(5)}"


def get_cvss_severity(score):
    if not score:
        return "NONE"
    score = float(score)
    if score < 4:
        return "LOW"
    elif score < 7:
        return "MEDIUM"
    elif score < 9:
        return "HIGH"
    else:
        return "CRITICAL"


class ReleaserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(user__username=username)


class Releaser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key_id = models.CharField(
        max_length=100, help_text="gpg --list-keys --keyid-format LONG"
    )
    key_url = models.URLField()

    objects = ReleaserManager()

    def natural_key(self):
        return (self.user.username,)

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.key_id} <{self.key_url}>"


class ReleaseChecklist(models.Model):
    when = models.DateTimeField()
    releaser = models.ForeignKey(Releaser, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    checklist_template = "checklists/release-skeleton.md"
    release_status_code = {v: k for k, v in Release.STATUS_REVERSE.items()}
    forum_post = None

    class Meta:
        abstract = True

    def __str__(self):
        return self.release.version_verbose

    @cached_property
    def blogpost_link(self, slug=None):
        if slug is None:
            slug = self.slug
        when = self.when.strftime("%Y/%b/%d").lower()
        return f"https://www.djangoproject.com/weblog/{when}/{slug}/"

    @cached_property
    def blogpost_template(self):
        return f"checklists/release_{self.status_reversed}_blogpost.md"

    @cached_property
    def blogpost_title(self):
        return f"Django {self.release.version_verbose} released"

    @cached_property
    def blogpost_summary(self):
        return f"Django {self.version} has been released!"

    @cached_property
    def is_pre_release(self):
        return False

    @cached_property
    def is_security_release(self):
        return "security" in self.slug

    @cached_property
    def slug(self):
        return f"django-{self.version.replace('.', '')}-released"

    @cached_property
    def status_reversed(self):
        if (release := getattr(self, "release", None)) is not None:
            return self.release_status_code[release.status]
        return "security"

    @cached_property
    def trove_classifier(self):
        result = "Development Status :: 5 - Production/Stable"
        if self.status_reversed == "alpha":
            result = "Development Status :: 3 - Alpha"
        elif self.status_reversed in ("beta", "rc"):
            result = "Development Status :: 4 - Beta"
        return result

    @cached_property
    def affected_releases(self):
        if (release := getattr(self, "release", None)) is not None:
            return [release]
        return []

    @cached_property
    def version(self):
        return enumerate_items(self.versions)

    @cached_property
    def versions(self):
        return [r.version for r in self.affected_releases]

    @cached_property
    def tags(self):
        return [r.feature_version.replace(".", "-") for r in self.affected_releases]

    def get_absolute_url(self):
        return reverse("checklists:release_checklist", kwargs={"version": self.version})

    def natural_key(self):
        return (self.release.version,) if self.release else (None,)

    def render_to_string(self, request=None):
        context = {
            "instance": self,
            "releaser": self.releaser,
            "slug": self.slug,
            "version": self.version,
            "title": self.__class__.__name__,
            "app_label": self._meta.app_label,
            **self.__dict__,
        }
        if (release := getattr(self, "release", None)) is not None:
            context["release"] = release
        if (data := getattr(self, "get_context_data", None)) is not None:
            context.update(data)
        return render_to_string(self.checklist_template, context, request=request)


class FeatureReleaseManager(models.Manager):
    def get_by_natural_key(self, version):
        return self.get(release__version=version)


class FeatureRelease(ReleaseChecklist):
    release = models.OneToOneField(Release, null=True, on_delete=models.SET_NULL)
    forum_post = models.URLField(blank=True)
    tagline = models.CharField(
        max_length=4096,
        help_text=(
            "Filler to use in the sentence <i>Django [version] [tagline] "
            "which you can read about in the release notes.</i></br>"
            "For example: <i>Django 5.1 brings <strong>a kaleidoscope of "
            "improvements</strong></i>."
        ),
    )
    highlights = models.TextField(blank=True)
    eom_release = models.ForeignKey(
        Release, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    eol_release = models.ForeignKey(
        Release, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    objects = FeatureReleaseManager()

    def __str__(self):
        return f"{self.version} {self.tagline}"

    @property
    def slug(self):
        return f"django-{self.version.replace('.', '')}-released"


class PreReleaseManager(models.Manager):
    def get_by_natural_key(self, version):
        return self.get(release__version=version)


class PreRelease(ReleaseChecklist):
    release = models.OneToOneField(Release, null=True, on_delete=models.SET_NULL)
    feature_release = models.ForeignKey(FeatureRelease, on_delete=models.CASCADE)

    objects = PreReleaseManager()

    @cached_property
    def blogpost_summary(self):
        return (
            f"Today Django {self.release.version_verbose}, a preview/testing package "
            f"for the upcoming Django {self.release.feature_version} release, is "
            "available."
        )

    @cached_property
    def forum_post(self):
        return self.feature_release.forum_post

    @cached_property
    def is_pre_release(self):
        return True

    @cached_property
    def slug(self):
        slug_version = self.release.feature_version.replace(".", "")
        return f"django-{slug_version}-{self.status_reversed}-released"


class BugFixReleaseManager(models.Manager):
    def get_by_natural_key(self, version):
        return self.get(release__version=version)


class BugFixRelease(ReleaseChecklist):
    release = models.OneToOneField(Release, null=True, on_delete=models.SET_NULL)

    objects = BugFixReleaseManager()

    slug = "bugfix-releases"

    @cached_property
    def blogpost_template(self):
        return "checklists/release_bugfix_blogpost.md"

    @cached_property
    def blogpost_title(self):
        return f"Django bugfix release issued: {self.version}"

    @cached_property
    def blogpost_summary(self):
        return (
            "Today the Django project issued a bugfix release for the "
            f"{self.release.feature_version} release series."
        )

    @cached_property
    def verbose_version(self):
        return self.version


class SecurityReleaseManager(models.Manager):
    def get_by_natural_key(self, when_iso):
        when = datetime.datetime.fromisoformat(when_iso)
        return self.get(when=when)


class SecurityRelease(ReleaseChecklist):
    checklist_template = "checklists/release-security-skeleton.md"
    slug = "security-releases"

    objects = SecurityReleaseManager()

    def natural_key(self):
        return (self.when.isoformat(),)

    def __str__(self):
        return f"Security release on {self.when}"

    @cached_property
    def blogpost_template(self):
        return "checklists/release_security_blogpost.md"

    @cached_property
    def blogpost_title(self):
        return f"Django security releases issued: {self.version}"

    @cached_property
    def blogpost_summary(self):
        enumerated_versions = enumerate_items(self.versions)
        fix = "fix" if len(self.versions) > 1 else "fixes"
        if (cves_length := len(self.cves)) == 1:
            cves_info = "one security issue"
        else:
            cves_info = f"{cves_length} security issues"
        return f"Django {enumerated_versions} {fix} {cves_info}"

    @cached_property
    def cves(self):
        return list(self.securityissue_set.all().order_by(*cve_sort_key()))

    @cached_property
    def cnas(self):
        return (
            self.securityissue_set.all()
            .order_by(*cve_sort_key())
            .values_list("cna", flat=True)
        )

    @cached_property
    def affected_branches(self):
        return ["main"] + [
            (
                r.feature_version
                if not r.is_pre_release
                else f"{r.feature_version} (currently at {r.get_status_display()} "
                "status)"
            )
            for r in self.affected_releases
        ]

    @cached_property
    def affected_releases(self):
        return sorted(
            {r for issue in self.securityissue_set.all() for r in issue.releases.all()},
            reverse=True,
        )

    @cached_property
    def versions(self):
        # Same as ReleaseChecklist, but leave pre-releases out.
        return [r.version for r in self.affected_releases if not r.is_pre_release]

    @cached_property
    def tags(self):
        return ["security"] + [
            r.feature_version.replace(".", "-")
            for r in self.affected_releases
            if not r.is_pre_release
        ]

    @cached_property
    def latest_release(self):
        return [r for r in self.affected_releases if not r.is_pre_release][0]

    @cached_property
    def hashes_by_versions(self):
        return [
            {
                "branch": sirt.release.feature_version,
                "cve": sirt.securityissue.cve_year_number,
                "hash": sirt.commit_hash,
            }
            for sirt in SecurityIssueReleasesThrough.objects.select_related(
                "securityissue", "release"
            )
            .filter(securityissue__release_id=self.id)
            .order_by(
                *cve_sort_key("securityissue__cve_year_number"),
                "-release__version",
            )
        ] + [
            {
                "branch": "main",
                "cve": issue.cve_year_number,
                "hash": issue.commit_hash_main,
            }
            for issue in self.cves
        ]

    def get_absolute_url(self):
        return reverse("checklists:securityrelease_checklist", kwargs={"pk": self.pk})


class SecurityIssueReleasesThroughManager(models.Manager):
    def get_by_natural_key(self, cve_year_number, version):
        return self.get(
            securityissue__cve_year_number=cve_year_number, release__version=version
        )


class SecurityIssueReleasesThrough(models.Model):
    securityissue = models.ForeignKey(
        "SecurityIssue", on_delete=models.CASCADE, verbose_name="Security Issue"
    )
    release = models.ForeignKey(Release, on_delete=models.CASCADE)
    commit_hash = models.CharField(
        max_length=128, default="", blank=True, db_index=True
    )

    objects = SecurityIssueReleasesThroughManager()

    def natural_key(self):
        return self.securityissue.natural_key() + (self.release.version,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["securityissue", "release"],
                name="unique_securityissue_release",
            ),
            models.UniqueConstraint(
                fields=["commit_hash"],
                name="unique_non_empty_commit_hash",
                condition=~models.Q(commit_hash=""),  # Exclude empty strings
            ),
        ]


class SecurityIssueManager(models.Manager):
    def get_by_natural_key(self, cve_year_number):
        return self.get(cve_year_number=cve_year_number)


class SecurityIssue(models.Model):
    cna = models.CharField(
        "CNA issuing the CVE ID for this issue.",
        max_length=128,
        default="DSF",
        choices=[(i, i) for i in ("DSF", "MITRE")],
    )
    cve_year_number = models.CharField(
        "CVE ID",
        max_length=1024,
        unique=True,
        default=get_cve_default,
        validators=[RegexValidator(regex=r"CVE-\d{4}-\d{4,5}")],
    )

    objects = SecurityIssueManager()
    severity = models.CharField(
        max_length=128,
        choices=[(i, i.capitalize()) for i in ("low", "moderate", "high")],
        default="moderate",
    )
    summary = models.CharField(
        max_length=1024,
        help_text=(
            "Markdown format. Single `backticks` for inline code. For the rst "
            "security archive entry, backticks are doubled automatically."
        ),
    )
    description = models.TextField(help_text=DESCRIPTION_HELP_TEXT)
    blogdescription = models.TextField(
        blank=True,
        verbose_name="Blog description",
        help_text=(
            "Markdown format. Single `backticks` for inline code. "
            "Copy from release notes, include severity sentence.",
        ),
    )
    reporter = models.CharField(max_length=1024, blank=True)
    remediator = models.CharField(max_length=1024, blank=True)
    discovery = models.CharField(
        max_length=128,
        choices=[(i, i.title()) for i in ("EXTERNAL", "INTERNAL", "USER", "UPSTREAM")],
        default="EXTERNAL",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_at = models.DateTimeField(null=True)
    confirmed_at = models.DateTimeField(null=True)

    # Deprecated. Left here for historical/migration purposes.
    other_type = models.CharField(
        max_length=1024, help_text="Deprecated.", default="Other"
    )
    attack_type = models.CharField(
        max_length=1024, help_text="Deprecated.", default="Remote"
    )

    # No choices for these, for now. Browse problem and impact types at the linked URLs.
    cve_type = models.TextField(
        "CWE Problem Type",
        help_text=(
            "Comma separated list of Common Weakness Enumeration "
            "(<strong>CWE</strong>) types.</br>MUST CONTAIN COLON SEPARATOR!</br>"
            "Browse available types at: "
            '<a href="https://cwe.mitre.org/">https://cwe.mitre.org/</a></br>'
            "Examples:</br><code>"
            "CWE-23: Relative Path Traversal</br>"
            "CWE-79: Improper Neutralization of Input During Web Page Generation "
            "('Cross-site Scripting')</br>"
            "CWE-89: Improper Neutralization of Special Elements used in an SQL "
            "Command "
            "('SQL Injection')</br>"
            "CWE-352: Cross-Site Request Forgery (CSRF)</br>"
            "CWE-117: Improper Output Neutralization for Logs</br>"
            "CWE-770: Allocation of Resources Without Limits or Throttling</code>"
        ),
    )
    impact = models.TextField(
        "CAPEC Impact Type",
        help_text=(
            "Comma separated list of Common Attack Pattern Enumeration and "
            "Classification (<strong>CAPEC</strong>) types.</br>MUST CONTAIN COLON "
            "SEPARATOR!</br>"
            'Browse available types at: <a href="https://capec.mitre.org/">'
            "https://capec.mitre.org/</a></br>Examples:</br><code>"
            "CAPEC-54: Query System for Information</br>"
            "CAPEC-62: Cross Site Request Forgery</br>"
            "CAPEC-63: Cross-Site Scripting (XSS)</br>"
            "CAPEC-66: SQL Injection</br>"
            "CAPEC-93: Log Injection-Tampering-Forging</br>"
            "CAPEC-491: Quadratic Data Expansion</code>"
        ),
    )

    # CVSS Scores.
    cvss_v3_vector_string = models.CharField(
        "CVSS v3.1 Vector String",
        max_length=256,
        blank=True,
        default="",
        help_text=(
            "CVSS v3.1 vector string. Example: "
            "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
        ),
    )
    cvss_v3_score = models.DecimalField(
        "CVSS v3.1 Score",
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Base score (0.0-10.0) from the CVSS v3.1 calculator.",
    )
    cvss_v4_vector_string = models.CharField(
        "CVSS v4.0 Vector String",
        max_length=256,
        blank=True,
        default="",
        help_text=(
            "CVSS v4.0 vector string. Example: "
            "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N"
        ),
    )
    cvss_v4_score = models.DecimalField(
        "CVSS v4.0 Score",
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Base score (0.0-10.0) from the CVSS v4.0 calculator.",
    )

    release = models.ForeignKey(
        SecurityRelease,
        help_text="Security Release that will fix this issue.",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    releases = models.ManyToManyField(Release, through=SecurityIssueReleasesThrough)
    commit_hash_main = models.CharField(
        max_length=128, default="", blank=True, db_index=True
    )

    def __str__(self):
        return self.cve_year_number

    def natural_key(self):
        return (self.cve_year_number,)

    @cached_property
    def cve_description(self):
        affected = format_releases_for_cves(self.releases.all())
        return (
            f"An issue was discovered in {affected}.\n{self.description}\n"
            "Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) "
            "were not evaluated and may also be affected.\n"
            f"Django would like to thank {self.reporter} for reporting this issue."
        )

    @cached_property
    def cve_html_description(self):
        return "".join(
            f"<p>{line.strip()}</p>"
            for line in urlize(self.cve_description).split("\n")
        )

    @property
    def cvss_v3_severity(self):
        return get_cvss_severity(self.cvss_v3_score)

    @property
    def cvss_v4_severity(self):
        return get_cvss_severity(self.cvss_v4_score)

    @property
    def headline_for_blogpost(self):
        return f"{self.cve_year_number}: {self.summary}"

    @property
    def headline_for_archive(self):
        when = self.release.when.strftime("%B %-d, %Y")
        return f"{when} - :cve:`{self.cve_year_number.replace('CVE-', '')}`"

    @property
    def hashes_by_branch(self):
        return sorted(
            [
                (sirt.release.feature_version, sirt.commit_hash)
                for sirt in SecurityIssueReleasesThrough.objects.select_related(
                    "release"
                ).filter(securityissue_id=self.id)
            ]
            + [("main", self.commit_hash_main)],
            reverse=True,
        )

    @property
    def cve_data(self):
        affected_unaffected_versions = []
        versions = []
        for release in self.releases.filter(status="f").order_by("-version"):
            versions.append(release.version)
            affected_unaffected_versions.extend(
                [
                    {
                        "status": "affected",
                        "version": f"{release.feature_version}",
                        "lessThan": release.version,
                        "versionType": "python",
                    },
                    {
                        "status": "unaffected",
                        "version": release.version,
                        "versionType": "python",
                    },
                ]
            )
        dates = {"timeline": []}
        if self.reported_at:
            dates["timeline"].append(
                {
                    "lang": "en",
                    "time": self.reported_at.isoformat(),
                    "value": "Initial report received.",
                },
            )
        if self.confirmed_at:
            dates["timeline"].append(
                {
                    "lang": "en",
                    "time": self.confirmed_at.isoformat(),
                    "value": "Vulnerability confirmed.",
                },
            )

        references = [
            {
                "url": "https://docs.djangoproject.com/en/dev/releases/security/",
                "name": "Django security archive",
                "tags": ["vendor-advisory"],
            },
            {
                "url": "https://groups.google.com/g/django-announce",
                "name": "Django releases announcements",
                "tags": ["mailing-list"],
            },
        ]
        credits = [
            {
                "lang": "en",
                "type": "reporter",
                "value": self.reporter,
            },
        ]
        if self.remediator:
            credits.append(
                {
                    "lang": "en",
                    "type": "remediation developer",
                    "value": self.remediator,
                }
            )

        if self.release:
            dates["datePublic"] = when = self.release.when.isoformat()
            dates["timeline"].append(
                {
                    "lang": "en",
                    "time": when,
                    "value": "Security release issued.",
                },
            )
            references.append(
                {
                    "url": self.release.blogpost_link,
                    "name": self.release.blogpost_title,
                    "tags": ["vendor-advisory"],
                }
            )
            credits.append(
                {
                    "lang": "en",
                    "type": "coordinator",
                    "value": self.release.releaser.user.get_full_name(),
                }
            )

        metrics = [
            {
                "other": {
                    "content": {
                        "value": self.severity,
                        "namespace": SEVERITY_LEVELS_DOCS,
                    },
                    "type": "Django severity rating",
                },
            },
        ]
        if self.cvss_v3_vector_string and self.cvss_v3_score is not None:
            metrics.append(
                {
                    "cvssV3_1": {
                        "version": "3.1",
                        "vectorString": self.cvss_v3_vector_string,
                        "baseScore": float(self.cvss_v3_score),
                        "baseSeverity": self.cvss_v3_severity,
                    },
                }
            )
        if self.cvss_v4_vector_string and self.cvss_v4_score is not None:
            metrics.append(
                {
                    "cvssV4_0": {
                        "version": "4.0",
                        "vectorString": self.cvss_v4_vector_string,
                        "baseScore": float(self.cvss_v4_score),
                        "baseSeverity": self.cvss_v4_severity,
                    },
                }
            )
        details = {
            "title": self.summary.replace("`", ""),
            "metrics": metrics,
            "descriptions": [
                {
                    "lang": "en",
                    "value": self.cve_description,
                    "supportingMedia": [
                        {
                            "type": "text/html",
                            "base64": False,
                            "value": self.cve_html_description,
                        },
                    ],
                },
            ],
            "affected": [
                {
                    "collectionURL": "https://pypi.org/project/Django/",
                    "defaultStatus": "unaffected",
                    "packageName": "django",
                    "product": "Django",
                    "repo": "https://github.com/django/django/",
                    "vendor": "djangoproject",
                    "versions": affected_unaffected_versions,
                }
            ],
            "references": references,
            "credits": credits,
            **dates,
            "source": {"discovery": self.discovery},
        }

        if self.cna != "DSF":
            return details

        return {
            "dataType": "CVE_RECORD",
            "dataVersion": "5.1",
            "cveMetadata": {
                "cveId": self.cve_year_number,
                "assignerOrgId": CNA_DSF_UUID,
                "state": "PUBLISHED",
            },
            "containers": {
                "cna": {
                    "providerMetadata": {"orgId": CNA_DSF_UUID},
                    "problemTypes": [
                        {
                            "descriptions": [
                                {
                                    "lang": "en",
                                    "cweId": self.cve_type.split(":")[0],
                                    "description": self.cve_type,
                                    "type": "CWE",
                                },
                            ],
                        },
                    ],
                    "impacts": [
                        {
                            "capecId": self.impact.split(":")[0],
                            "descriptions": [
                                {
                                    "lang": "en",
                                    "value": self.impact,
                                },
                            ],
                        },
                    ],
                    **details,
                },
            },
        }

    @property
    def cve_json(self):
        return json.dumps(self.cve_data, sort_keys=True, indent=2)

    @property
    def cve_minified_json(self):
        return json.dumps(self.cve_data, sort_keys=True, separators=(",", ":"))

    def get_absolute_url(self):
        return reverse("checklists:cve_json_record", args=[self.cve_year_number])
