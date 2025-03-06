import datetime
from unittest import skip

from django.contrib import admin
from django.core.files.base import ContentFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils.safestring import SafeString

from members.models import MEMBERSHIP_LEVELS, PLATINUM_MEMBERSHIP, CorporateMember

from .models import Release, upload_to_artifact, upload_to_checksum
from .templatetags.date_format import isodate
from .templatetags.release_notes import get_latest_micro_release, release_notes


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

    def test_isodate(self):
        self.assertEqual(isodate("2005-07-21"), "July 21, 2005")

    def test_isodate_explicit_format(self):
        self.assertEqual(isodate("2005-07-21", "Ymd"), "20050721")
        self.assertEqual(isodate("2005-07-21", "d/m/Y"), "21/07/2005")

    @override_settings(LANGUAGE_CODE="nn")
    def test_isodate_translated(self):
        self.assertEqual(isodate("2005-07-21"), "21. juli 2005")


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


class ReleaseUploadToTestCase(SimpleTestCase):
    def test_upload_to_artifact(self):
        for version, filename, expected in [
            ("5.2", "django-5.2.tar.gz", "releases/5.2/django-5.2.tar.gz"),
            ("5.2", "django-5.2.tar.xz", "releases/5.2/django-5.2.tar.xz"),
            ("5.2", "Django-5.2.tar.gz", "releases/5.2/Django-5.2.tar.gz"),
            ("5.2", "DJANGO-5.2.tar.gz", "releases/5.2/DJANGO-5.2.tar.gz"),
            ("5.2.1", "django-5.2.1.tar.gz", "releases/5.2/django-5.2.1.tar.gz"),
            ("5.2a1", "django-5.2a1.tar.gz", "releases/5.2/django-5.2a1.tar.gz"),
            ("5.2b2", "django-5.2b2.tar.gz", "releases/5.2/django-5.2b2.tar.gz"),
            ("5.2", "django-5.2-py3-none.whl", "releases/5.2/django-5.2-py3-none.whl"),
            ("5.2", "Django-5.2-py3-none.whl", "releases/5.2/Django-5.2-py3-none.whl"),
            ("5.2", "DJANGO-5.2-py3-none.whl", "releases/5.2/DJANGO-5.2-py3-none.whl"),
            (
                "5.2.1",
                "django-5.2.1-py3-none.whl",
                "releases/5.2/django-5.2.1-py3-none.whl",
            ),
            (
                "5.2a1",
                "django-5.2a1-py3-none.whl",
                "releases/5.2/django-5.2a1-py3-none.whl",
            ),
            (
                "5.2b2",
                "django-5.2b2-py3-none.whl",
                "releases/5.2/django-5.2b2-py3-none.whl",
            ),
        ]:
            with self.subTest(version=version, filename=filename):
                self.assertEqual(
                    upload_to_artifact(Release(version=version), filename=filename),
                    expected,
                )

    def test_upload_to_checksum(self):
        for version, expected in [
            ("5.2", "pgp/Django-5.2.checksum.txt"),
            ("5.2.1", "pgp/Django-5.2.1.checksum.txt"),
            ("5.2a1", "pgp/Django-5.2a1.checksum.txt"),
            ("5.2b2", "pgp/Django-5.2b2.checksum.txt"),
        ]:
            with self.subTest(version=version):
                self.assertEqual(
                    # filename should not matter
                    upload_to_checksum(Release(version=version), filename=None),
                    expected,
                )


class ReleaseAdminFormTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form_class = admin.site.get_model_admin(Release).get_form(request=None)

    def test_non_published_releases_tarball_not_required(self):
        form = self.form_class({"version": "1.0", "date": None})
        self.assertTrue(form.is_valid(), form.errors)

    def test_published_releases_tarball_required(self):
        form = self.form_class({"version": "1.0", "date": "2008-09-03"})
        self.assertFormError(
            form,
            "tarball",
            "This field is required when the release is active by having a date",
        )

    @skip  # TODO (restore feature or delete test)
    def test_artifact_file_inputs_have_extension_hint(self):
        form = self.form_class(auto_id=None)  # auto_id=None makes testing easier
        self.assertHTMLEqual(
            form["tarball"].as_widget(),
            '<input type="file" name="tarball" accept=".tar.gz">',
        )
        self.assertHTMLEqual(
            form["wheel"].as_widget(), '<input type="file" name="wheel" accept=".whl">'
        )
        self.assertHTMLEqual(
            form["checksum"].as_widget(),
            '<input type="file" name="checksum" accept=".txt">',
        )

    def test_file_upload_renames_correctly(self):
        data = {"version": "1.2.3"}
        files = {
            # The content of the files doesn't matter
            "tarball": ContentFile(b".", name="django-1.2.3.tar.gz"),
            "wheel": ContentFile(b".", name="django-1.2.3-py3-none-any.whl"),
            "checksum": ContentFile(b".", name="some-random-name.checksum.txt"),
        }
        form = self.form_class(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        release = form.save()
        self.assertEqual(release.tarball.name, "releases/1.2/django-1.2.3.tar.gz")
        self.assertEqual(
            release.wheel.name, "releases/1.2/django-1.2.3-py3-none-any.whl"
        )
        self.assertEqual(release.checksum.name, "pgp/Django-1.2.3.checksum.txt")


class RedirectViewTestCase(TestCase):
    def test_redirect(self):
        Release.objects.create(
            version="1.0",
            tarball="test.tar.gz",
            wheel="test.whl",
            checksum="test.checksum.txt",
        )

        for kind, url in [
            ("tarball", "/m/test.tar.gz"),
            ("wheel", "/m/test.whl"),
            ("checksum", "/m/test.checksum.txt"),
        ]:
            response = self.client.get(f"/download/1.0/{kind}/")
            with self.subTest(kind=kind):
                self.assertRedirects(response, url, 301, fetch_redirect_response=False)

    def test_redirect_404(self):
        Release.objects.create(version="1.0")

        for kind in ["tarball", "wheel", "checksum"]:
            response = self.client.get(f"/download/1.0/{kind}/")
            with self.subTest(kind=kind):
                self.assertEqual(response.status_code, 404)


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
            description=f"Some notes about this {level_name} member",
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
            lambda m: f'<a href="{m.url}" title="{m.display_name}">{m.description}</a>'
        )
        for member in members:
            if member.membership_level < PLATINUM_MEMBERSHIP:
                self.assertNotContains(response, member.display_name)
                self.assertNotContains(response, member.url)
                self.assertNotContains(response, member.description)
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
            self.assertNotContains(response, member.description)
