import datetime

from django.contrib.redirects.models import Redirect
from django.test import TestCase
from django.urls import reverse
from django.utils.safestring import SafeString

from members.models import MEMBERSHIP_LEVELS, PLATINUM_MEMBERSHIP, CorporateMember

from .models import Release, create_releases_up_to_1_5
from .templatetags.release_notes import get_latest_micro_release, release_notes


class LegacyURLsTests(TestCase):
    fixtures = ["redirects-downloads"]  # provided by the legacy app

    def test_legacy_redirects(self):
        # Save list of redirects, then wipe them
        redirects = list(Redirect.objects.values_list("old_path", "new_path"))
        Redirect.objects.all().delete()
        # Ensure the releases app faithfully reproduces the redirects
        create_releases_up_to_1_5()
        for old_path, new_path in redirects:
            response = self.client.get(old_path, follow=False)
            location = response.get("Location", "")
            if location.startswith("http://testserver"):
                location = location[17:]
            self.assertEqual(location, new_path)
            self.assertEqual(response.status_code, 301)


class TestTemplateTags(TestCase):
    def test_get_latest_micro_release(self):
        Release.objects.create(major=1, minor=8, micro=0, is_lts=True, version="1.8")
        Release.objects.create(major=1, minor=8, micro=1, is_lts=True, version="1.8.1")

        self.assertEqual(get_latest_micro_release("1.8"), "1.8.1")
        self.assertEqual(get_latest_micro_release("1.4"), None)

    def test_release_notes(self):
        output = release_notes("1.8")
        self.assertIsInstance(output, SafeString)
        self.assertEqual(
            output,
            '<a href="http://docs.djangoproject.localhost:8000/en/1.8/releases/1.8/">'
            "Online documentation</a>",
        )
        self.assertEqual(
            release_notes("1.8", show_version=True),
            '<a href="http://docs.djangoproject.localhost:8000/en/1.8/releases/1.8/">'
            "1.8 release notes</a>",
        )

    def test_release_notes_1_10(self):
        output = release_notes("1.10")
        self.assertIsInstance(output, SafeString)
        self.assertEqual(
            output,
            '<a href="http://docs.djangoproject.localhost:8000/en/1.10/releases/1.10/">'
            "Online documentation</a>",
        )
        self.assertEqual(
            release_notes("1.10", show_version=True),
            '<a href="http://docs.djangoproject.localhost:8000/en/1.10/releases/1.10/">'
            "1.10 release notes</a>",
        )


class TestReleaseManager(TestCase):
    @classmethod
    def setUpTestData(cls):
        today = datetime.date.today()
        day = datetime.timedelta(1)
        Release.objects.create(
            version="1.4",
            is_lts=True,
            date=today - 450 * day,
            eol_date=today + 50 * day,
        )
        Release.objects.create(
            version="1.5", date=today - 350 * day, eol_date=today - 150 * day
        )
        Release.objects.create(
            version="1.6", date=today - 250 * day, eol_date=today - 50 * day
        )
        Release.objects.create(
            version="1.7", date=today - 150 * day, eol_date=today + 50 * day
        )
        Release.objects.create(
            version="1.8a1", date=today - 80 * day, eol_date=today - 65 * day
        )
        Release.objects.create(
            version="1.8b1",
            is_lts=True,
            date=today - 65 * day,
            eol_date=today - 50 * day,
        )
        Release.objects.create(
            version="1.8", is_lts=True, date=today - 50 * day, eol_date=today
        )
        Release.objects.create(version="1.8.1", is_lts=True, date=today, eol_date=None)
        Release.objects.create(version="1.9", date=None, eol_date=None)

    def test_active(self):
        active_versions = Release.objects.active().values_list("version", flat=True)
        self.assertEqual(list(active_versions), ["1.8.1", "1.7", "1.4"])

    def test_supported(self):
        supported_versions = Release.objects.supported().values_list(
            "version", flat=True
        )
        self.assertEqual(list(supported_versions), ["1.8.1", "1.7", "1.4"])

    def test_unsupported(self):
        unsupported_versions = [r.version for r in Release.objects.unsupported()]
        self.assertEqual(unsupported_versions, ["1.6", "1.5"])

    def test_current(self):
        self.assertEqual(Release.objects.current().version, "1.8.1")
        Release.objects.filter(version="1.8.1").delete()
        self.assertEqual(Release.objects.current().version, "1.7")

    def test_previous(self):
        self.assertEqual(Release.objects.previous().version, "1.7")

    def test_lts(self):
        lts_versions = Release.objects.lts().values_list("version", flat=True)
        self.assertEqual(list(lts_versions), ["1.8.1", "1.4"])

    def test_current_lts(self):
        self.assertEqual(Release.objects.current_lts().version, "1.8.1")
        Release.objects.filter(version="1.8.1").delete()
        self.assertEqual(Release.objects.current_lts().version, "1.4")

    def test_previous_lts(self):
        self.assertEqual(Release.objects.previous_lts().version, "1.4")
        Release.objects.filter(version="1.8.1").delete()
        self.assertEqual(Release.objects.previous_lts(), None)

    def test_preview(self):
        self.assertEqual(Release.objects.preview(), None)
        Release.objects.create(
            version="1.9b2", date=datetime.date.today(), eol_date=None
        )
        self.assertEqual(Release.objects.preview().version, "1.9b2")


class CorporateMembersTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.today = today = datetime.date.today()
        day = datetime.timedelta(1)
        Release.objects.create(
            version="1.7", date=today - 150 * day, eol_date=today + 50 * day
        )
        Release.objects.create(
            version="1.8", is_lts=True, date=today - 50 * day, eol_date=None
        )

    def make_member(self, level, level_name):
        member = CorporateMember.objects.create(
            display_name=f"{level_name} Member",
            url=f"https://{level_name.lower()}.example.com",
            membership_level=level,
            notes=f"Some notes about this {level_name} member",
        )
        # ensure each member is included in `for_public_display`
        member.invoice_set.create(
            amount=level * 1000,
            sent_date=self.today,
            paid_date=self.today,
            expiration_date=self.today + datetime.timedelta(days=30),
        )
        return member

    def test_diamond_and_platinum_members_shown(self):
        members = [
            self.make_member(level, level_name)
            for level, level_name in MEMBERSHIP_LEVELS
        ]

        response = self.client.get(reverse("download"))

        self.assertContains(response, "<h2>Diamond and Platinum Members</h2>")
        member_link = (
            lambda m: f'<a href="{m.url}" title="{m.display_name}">{m.notes}</a>'
        )
        for member in members:
            if member.membership_level < PLATINUM_MEMBERSHIP:
                self.assertNotContains(response, member.display_name)
                self.assertNotContains(response, member.url)
                self.assertNotContains(response, member.notes)
            else:
                self.assertContains(response, member_link(member), html=True)

    def test_no_diamond_and_platinum_members(self):
        members = [
            self.make_member(level, level_name)
            for level, level_name in MEMBERSHIP_LEVELS
            if level < PLATINUM_MEMBERSHIP
        ]

        response = self.client.get(reverse("download"))

        self.assertNotContains(response, "<h2>Diamond and Platinum Members</h2>")
        for member in members:
            self.assertNotContains(response, member.display_name)
            self.assertNotContains(response, member.url)
            self.assertNotContains(response, member.notes)
