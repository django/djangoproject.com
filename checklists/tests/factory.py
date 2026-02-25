import random
from datetime import date, timedelta
from uuid import uuid4

from django.contrib.auth.models import Permission, User
from django.utils.timezone import now

from checklists.models import (
    FeatureRelease,
    Releaser,
    SecurityIssue,
    SecurityRelease,
)
from releases.models import Release


class Factory:
    def make_user(self, perm_names=None, **kwargs):
        username = kwargs.setdefault("username", f"username-{uuid4()}")
        kwargs.setdefault("email", f"{username}@example.com")
        password = kwargs.setdefault("password", "Passw0rd!")
        user = User.objects.create_user(**kwargs)
        user.raw_password = password
        if perm_names:
            perms = Permission.objects.filter(codename__in=perm_names)
            assert len(perms) == len(perm_names)
            user.user_permissions.add(*perms)
        return user

    def make_release(self, **kwargs):
        version = kwargs.setdefault("version", "5.2")
        kwargs.setdefault("date", date(2025, 4, 2))
        kwargs.setdefault("is_lts", version.split(".", 1)[1].startswith("2"))
        return Release.objects.create(**kwargs)

    def make_releaser(self, user=None):
        if user is None:
            user = self.make_user(
                username=f"releaser-{uuid4()}", first_name="Merry", last_name="Pippin"
            )
        return Releaser.objects.create(
            user=user,
            key_id="1234567890ABCDEF",
            key_url="https://github.com/releaser.gpg",
        )

    def make_checklist(self, checklist_class, releaser=None, when=None, **kwargs):
        if releaser is None:
            releaser = self.make_releaser()
        if when is None:
            when = now() + timedelta(days=10)
        return checklist_class.objects.create(releaser=releaser, when=when, **kwargs)

    def make_feature_release_checklist(self, version, tagline="brings a collection"):
        future = now() + timedelta(days=75)
        release = self.make_release(version=version, date=future)
        return self.make_checklist(
            FeatureRelease, when=future, tagline=tagline, release=release
        )

    def make_security_checklist(self, with_issues=True, releases=None, **kwargs):
        checklist = self.make_checklist(SecurityRelease, **kwargs)
        if releases is None:
            releases = [self.make_release()]
        if releases != []:
            self.make_security_issue(checklist, releases=releases)
        return checklist

    def make_security_issue(
        self,
        security_release_checklist=None,
        releases=None,
        *,
        cve_year_number=None,
        commit_hash_main="",
        reported_at=None,
        confirmed_at=None,
        reporter="",
        remediator="",
        cna="MITRE",
        **kwargs,
    ):
        if security_release_checklist is None:
            security_release_checklist = self.make_security_checklist(releases=[])
        if cve_year_number is None:  # make a random one to avoid collision
            current_year = now().year
            random_5digit = random.randint(10000, 100000)
            cve_year_number = f"CVE-{current_year}-{random_5digit}"

        issue = SecurityIssue.objects.create(
            release=security_release_checklist,
            cve_year_number=cve_year_number,
            commit_hash_main=commit_hash_main,
            reported_at=reported_at,
            confirmed_at=confirmed_at,
            reporter=reporter,
            remediator=remediator,
            cna=cna,
            **kwargs,
        )
        if releases is None:
            releases = [self.make_release()]
        issue.releases.add(*releases)
        return issue
