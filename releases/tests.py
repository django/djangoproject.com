import datetime
import re

from django.contrib import admin
from django.core.exceptions import ValidationError
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
            is_active=True,
            is_lts=True,
            date=today - 450 * day,
            eol_date=today + 50 * day,
        )
        Release.objects.create(
            version="1.5",
            is_active=True,
            date=today - 350 * day,
            eol_date=today - 150 * day,
        )
        Release.objects.create(
            version="1.6",
            is_active=True,
            date=today - 250 * day,
            eol_date=today - 50 * day,
        )
        Release.objects.create(
            version="1.7",
            is_active=True,
            date=today - 150 * day,
            eol_date=today + 50 * day,
        )
        Release.objects.create(
            version="1.8a1",
            is_active=True,
            date=today - 80 * day,
            eol_date=today - 65 * day,
        )
        Release.objects.create(
            version="1.8b1",
            is_lts=True,
            is_active=True,
            date=today - 65 * day,
            eol_date=today - 50 * day,
        )
        Release.objects.create(
            version="1.8",
            is_lts=True,
            is_active=True,
            date=today - 50 * day,
            eol_date=today,
        )
        Release.objects.create(
            version="1.8.1", is_active=True, is_lts=True, date=today, eol_date=None
        )
        Release.objects.create(version="1.9", is_active=True, date=None, eol_date=None)
        Release.objects.create(
            version="1.10", is_active=False, date=today, eol_date=None
        )

    def test_published(self):
        active_versions = Release.objects.published().values_list("version", flat=True)
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
            version="1.9b2", is_active=True, date=datetime.date.today(), eol_date=None
        )
        self.assertEqual(Release.objects.preview().version, "1.9b2")


class ReleaseTestCase(TestCase):
    def test_is_published(self):
        today = datetime.date.today()
        future = today + datetime.timedelta(days=1)
        past = today - datetime.timedelta(days=1)
        cases = [
            ({"date": None, "is_active": True}, False),
            ({"date": None, "is_active": False}, False),
            ({"date": today, "is_active": True}, True),
            ({"date": today, "is_active": False}, False),
            ({"date": past, "is_active": True}, True),
            ({"date": past, "is_active": False}, False),
            ({"date": future, "is_active": True}, False),
            ({"date": future, "is_active": False}, False),
        ]
        for i, (params, expected) in enumerate(cases):
            with self.subTest(**params, saved=False):
                release = Release(version="1.0", **params)
                self.assertIs(release.is_published, expected)
            with self.subTest(**params, saved=True):
                release = Release.objects.create(version=f"{i}.0", **params)
                self.assertIs(release.is_published, expected)

    def test_save_sets_eol_date(self):
        today = datetime.date.today()
        future = today + datetime.timedelta(days=1)
        past = today - datetime.timedelta(days=1)
        cases = [
            ({"date": None, "is_active": True}, None),
            ({"date": None, "is_active": False}, None),
            ({"date": today, "is_active": True}, today),
            ({"date": today, "is_active": False}, None),
            ({"date": past, "is_active": True}, past),
            ({"date": past, "is_active": False}, None),
            ({"date": future, "is_active": True}, future),
            ({"date": future, "is_active": False}, None),
        ]
        for i, (params, expected_eol_date) in enumerate(cases):
            previous = Release.objects.create(version=f"{i}.1.1")
            release = Release(version=f"{i}.1.2")
            for k, v in params.items():
                setattr(release, k, v)
            release.save()
            previous.refresh_from_db()
            with self.subTest(**params):
                self.assertEqual(previous.eol_date, expected_eol_date)

    def test_save_eol_date_pre_releases(self):
        other_release = Release.objects.create(version="5.1.7", is_active=True)
        today = datetime.date.today()
        cases = [
            ("5.1.1", "5.2a1"),
            ("5.2a1", "5.2a2"),
            ("5.2a2", "5.2b1"),
            ("5.2b1", "5.2rc1"),
            ("5.2rc1", "5.2"),
            ("5.2", "5.2.1"),
        ]
        for previous_version, next_version in cases:
            with self.subTest(msg=f"{previous_version} -> {next_version}"):
                previous_release, _ = Release.objects.get_or_create(
                    version=previous_version,
                    is_active=True,
                )
                self.assertIsNone(previous_release.eol_date)
                next_release = Release.objects.create(
                    version=next_version, is_active=True
                )
                previous_release.refresh_from_db()
                other_release.refresh_from_db()
                if next_release.version_tuple[-2:] != ("alpha", 1):
                    self.assertEqual(previous_release.eol_date, today)
                self.assertIsNone(next_release.eol_date)
                self.assertIsNone(other_release.eol_date)


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
            ("5.2rc3", "django-5.2rc3.tar.gz", "releases/5.2/django-5.2rc3.tar.gz"),
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
        today = datetime.date.today()
        future = today + datetime.timedelta(days=1)
        past = today - datetime.timedelta(days=1)
        cases = [
            ({"date": None, "is_active": True}, False),
            ({"date": None, "is_active": False}, False),
            ({"date": today, "is_active": True}, True),
            ({"date": today, "is_active": False}, False),
            ({"date": past, "is_active": True}, True),
            ({"date": past, "is_active": False}, False),
            ({"date": future, "is_active": True}, False),
            ({"date": future, "is_active": False}, False),
        ]
        for params, tarball_required in cases:
            form = self.form_class({"version": "1.0", **params})
            with self.subTest(**params):
                self.assertIs(form.is_valid(), not tarball_required, form.errors)

    def test_published_release_tarball_required(self):
        form = self.form_class(
            {"version": "1.0", "date": "2008-09-03", "is_active": True}
        )
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form,
            "tarball",
            "This field is required when the release is active.",
        )

    def test_checksum_required_if_tarball_provided(self):
        form = self.form_class(
            data={"version": "1.0", "date": None},
            files={"tarball": ContentFile(b".", name="django-1.0.tar.gz")},
        )
        self.assertFormError(
            form,
            "checksum",
            "This field is required when an artifact has been uploaded.",
        )

    def test_checksum_required_if_wheel_provided(self):
        form = self.form_class(
            data={"version": "1.0", "date": None},
            files={"wheel": ContentFile(b".", name="django-1.0-py3-none-any.whl")},
        )
        self.assertFormError(
            form,
            "checksum",
            "This field is required when an artifact has been uploaded.",
        )

    def test_artifact_filename_validation_valid(self):
        for artifact, version, filename in [
            ("tarball", "1.0", "django-1.0.tar.gz"),
            ("tarball", "1.0", "Django-1.0.tar.gz"),
            ("tarball", "1.10", "django-1.10.tar.gz"),
            ("tarball", "1.2.3", "django-1.2.3.tar.gz"),
            ("tarball", "1.0a1", "django-1.0a1.tar.gz"),
            ("tarball", "1.0b1", "django-1.0b1.tar.gz"),
            ("tarball", "1.0rc1", "django-1.0rc1.tar.gz"),
            ("wheel", "1.0", "django-1.0-py3-none-any.whl"),
            ("wheel", "1.0", "Django-1.0-py3-none-any.whl"),
            ("wheel", "1.10", "django-1.10-py3-none-any.whl"),
            ("wheel", "1.2.3", "django-1.2.3-py3-none-any.whl"),
            ("wheel", "1.0a1", "django-1.0a1-py3-none-any.whl"),
            ("wheel", "1.0b1", "django-1.0b1-py3-none-any.whl"),
            ("wheel", "1.0rc1", "django-1.0rc1-py3-none-any.whl"),
        ]:
            form = self.form_class(
                data={"version": version},
                files={
                    artifact: ContentFile(b".", name=filename),
                    "checksum": ContentFile(b".", name="checksum.txt"),
                },
            )
            with self.subTest(version=version, filename=filename):
                self.assertFormError(form, artifact, [])

    def test_artifact_filename_validation_invalid(self):
        for artifact, version, filename in [
            ("tarball", "1.0", "django-1.2.tar.gz"),
            ("tarball", "1.0", "django-1.0.1.tar.gz"),
            ("tarball", "1.0.1", "django-1.0.tar.gz"),
            ("tarball", "1.0a1", "django-1.0.tar.gz"),
            ("tarball", "1.0", "django-1.0-py3-none-any.tar.gz"),
            ("tarball", "1.0", "django-1.0-py3-none-any.whl"),
            ("tarball", "1.0", "django-1.0.tar.xz"),
            ("wheel", "1.0", "django-1.2-py3-none-any.whl"),
            ("wheel", "1.0", "django-1.0.1-py3-none-any.whl"),
            ("wheel", "1.0.1", "django-1.0-py3-none-any.whl"),
            ("wheel", "1.0a1", "django-1.0-py3-none-any.whl"),
            ("wheel", "1.0", "django-1.0.whl"),
            ("wheel", "1.0", "django-1.0.tar.gz"),
        ]:
            form = self.form_class(
                data={"version": version, "date": None},
                files={
                    artifact: ContentFile(b".", name=filename),
                    "checksum": ContentFile(b".", name="doesntmatter.txt"),
                },
            )
            if artifact == "tarball":
                pattern = rf"^[Dd]jango-{re.escape(version)}\.tar\.gz$"
            else:
                pattern = rf"^[Dd]jango-{re.escape(version)}\-py3\-none\-any\.whl$"
            error = f"Filename {filename} does not match pattern {pattern}."
            with self.subTest(version=version, filename=filename):
                self.assertFormError(form, artifact, error)

    def test_artifact_name_validation_with_full_path(self):
        release = Release(
            version="1.0",
            checksum="checksu.txt",
            tarball="releases/1.0/django-1.0.tar.gz",
        )
        try:
            release.full_clean()
        except ValidationError as e:
            self.fail(f"Unexpected validation error {e}")

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
            '<input type="file" name="checksum" accept=".asc,.txt">',
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
            is_active=True,
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

    def test_redirect_is_not_published(self):
        today = datetime.date.today()
        future = today + datetime.timedelta(days=1)
        past = today - datetime.timedelta(days=1)
        cases = [
            ({"date": None, "is_active": True}, 301),
            ({"date": None, "is_active": False}, 301),
            ({"date": today, "is_active": True}, 301),
            ({"date": today, "is_active": False}, 301),
            ({"date": past, "is_active": True}, 301),
            ({"date": past, "is_active": False}, 301),
            ({"date": future, "is_active": True}, 301),
            ({"date": future, "is_active": False}, 301),
        ]
        for i, (params, status_code) in enumerate(cases):
            Release.objects.create(
                version=f"{i}.0",
                tarball="test.tar.gz",
                wheel="test.whl",
                checksum="test.checksum.txt",
                **params,
            )
            for kind in ["tarball", "wheel", "checksum"]:
                response = self.client.get(f"/download/{i}.0/{kind}/")
                with self.subTest(kind=kind, **params):
                    self.assertEqual(response.status_code, status_code)


class CorporateMembersTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.today = today = datetime.date.today()
        day = datetime.timedelta(1)
        Release.objects.create(
            version="1.7",
            is_active=True,
            date=today - 150 * day,
            eol_date=today + 50 * day,
        )
        Release.objects.create(
            version="1.8",
            is_active=True,
            is_lts=True,
            date=today - 50 * day,
            eol_date=None,
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

        self.assertContains(response, "<h3>Diamond and Platinum Members</h3>")
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

        self.assertNotContains(response, "<h3>Diamond and Platinum Members</h3>")
        for member in members:
            self.assertNotContains(response, member.display_name)
            self.assertNotContains(response, member.url)
            self.assertNotContains(response, member.description)
