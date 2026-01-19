from datetime import date, datetime

from django.test import TestCase

from checklists.templatetags.checklist_extras import (
    enumerate_cves,
    enumerate_items,
    format_release_for_cve,
    format_releases_for_cves,
    format_version_for_blogpost,
    format_version_tuple,
    format_versions_for_blogpost,
    next_feature_version,
    next_release_date,
    next_version,
    next_version_tuple,
    rst_backticks,
    rst_underline_for_headline,
    stub_release_notes_title,
)
from checklists.tests.factory import Factory
from releases.models import Release


class EnumerateItemsTestCase(TestCase):
    def test_empty_list(self):
        result = enumerate_items([])
        self.assertEqual(result, "")

    def test_single_item(self):
        result = enumerate_items(["Django 5.2"])
        self.assertEqual(result, "Django 5.2")

    def test_two_items(self):
        """No comma for two items."""
        result = enumerate_items(["Django 5.2", "Django 5.1.1"])
        self.assertEqual(result, "Django 5.2 and Django 5.1.1")

    def test_three_items(self):
        """Oxford comma for three or more items."""
        result = enumerate_items(["Django 5.2", "Django 5.1.1", "Django 4.2.8"])
        self.assertEqual(result, "Django 5.2, Django 5.1.1, and Django 4.2.8")

    def test_four_items(self):
        result = enumerate_items(["5.2", "5.1.1", "4.2.8", "3.2.23"])
        self.assertEqual(result, "5.2, 5.1.1, 4.2.8, and 3.2.23")

    def test_with_formatter_function(self):
        def uppercase(item):
            return item.upper()

        result = enumerate_items(["a", "b", "c"], item_formatter=uppercase)
        self.assertEqual(result, "A, B, and C")


class EnumerateCvesTestCase(TestCase):
    factory = Factory()

    def test_enumerate_cves_with_cve_ids(self):
        cve1 = self.factory.make_security_issue(
            cve_year_number="CVE-2024-12345", releases=[]
        )
        cve2 = self.factory.make_security_issue(
            cve_year_number="CVE-2024-12346", releases=[]
        )
        cve3 = self.factory.make_security_issue(
            cve_year_number="CVE-2024-12347", releases=[]
        )

        result = enumerate_cves([cve1, cve2, cve3])
        self.assertEqual(result, "CVE-2024-12345, CVE-2024-12346, and CVE-2024-12347")

    def test_enumerate_cves_with_severity(self):
        cve1 = self.factory.make_security_issue(severity="high", releases=[])
        cve2 = self.factory.make_security_issue(severity="medium", releases=[])
        cve3 = self.factory.make_security_issue(severity="low", releases=[])

        result = enumerate_cves([cve1, cve2, cve3], "severity")
        self.assertEqual(result, "high, medium, and low")

    def test_enumerate_cves_single(self):
        cve = self.factory.make_security_issue(cve_year_number="CVE-2024-12345")
        result = enumerate_cves([cve])
        self.assertEqual(result, "CVE-2024-12345")


class NextVersionTestCase(TestCase):
    def test_next_micro_version(self):
        release = Release.objects.create(version="5.1.3")
        result = next_version(release)
        self.assertEqual(result, "5.1.4")

    def test_next_version_from_zero(self):
        release = Release.objects.create(version="5.2")
        result = next_version(release)
        self.assertEqual(result, "5.2.1")

    def test_next_version_high_number(self):
        release = Release.objects.create(version="4.2.15")
        result = next_version(release)
        self.assertEqual(result, "4.2.16")


class NextFeatureVersionTestCase(TestCase):
    def test_next_feature_from_minor(self):
        release = Release.objects.create(version="4.0.5")
        result = next_feature_version(release)
        self.assertEqual(result, "4.1")

    def test_next_feature_from_dot_zero(self):
        release = Release.objects.create(version="4.1")
        result = next_feature_version(release)
        self.assertEqual(result, "4.2")

    def test_next_feature_high_minor(self):
        release = Release.objects.create(version="5.2.9")
        result = next_feature_version(release)
        self.assertEqual(result, "6.0")


class NextVersionTupleTestCase(TestCase):
    def test_next_version_tuple_basic(self):
        release = Release.objects.create(version="3.2.10")
        result = next_version_tuple(release)
        self.assertEqual(result, (3, 2, 11, "alpha", 0))

    def test_next_version_tuple_from_zero(self):
        release = Release.objects.create(version="3.2")
        result = next_version_tuple(release)
        self.assertEqual(result, (3, 2, 1, "alpha", 0))


class FormatVersionTupleTestCase(TestCase):
    def test_format_version_tuple_final(self):
        release = Release.objects.create(version="5.0.10")
        result = format_version_tuple(release.version_tuple)
        self.assertEqual(result, '(5, 0, 10, "final", 0)')

    def test_format_version_tuple_dot_zero(self):
        release = Release.objects.create(version="5.0")
        result = format_version_tuple(release.version_tuple)
        self.assertEqual(result, '(5, 0, 0, "final", 0)')

    def test_format_version_tuple_alpha(self):
        release = Release.objects.create(version="6.0a1")
        result = format_version_tuple(release.version_tuple)
        self.assertEqual(result, '(6, 0, 0, "alpha", 1)')

    def test_format_version_tuple_beta(self):
        release = Release.objects.create(version="6.1b2")
        result = format_version_tuple(release.version_tuple)
        self.assertEqual(result, '(6, 1, 0, "beta", 2)')

    def test_format_version_tuple_rc(self):
        release = Release.objects.create(version="5.1rc1")
        result = format_version_tuple(release.version_tuple)
        self.assertEqual(result, '(5, 1, 0, "rc", 1)')


class StubReleaseNotesTitleTestCase(TestCase):
    def test_stub_release_notes_title_final(self):
        release = Release.objects.create(version="6.2.3")
        result = stub_release_notes_title(release)
        expected = (
            "==========================\n"
            "Django 6.2.3 release notes\n"
            "=========================="
        )
        self.assertEqual(result, expected)

    def test_stub_release_notes_title_alpha(self):
        release = Release.objects.create(version="6.2a1")
        result = stub_release_notes_title(release)
        expected = (
            "==========================\n"
            "Django 6.2a1 release notes\n"
            "=========================="
        )
        self.assertEqual(result, expected)

    def test_stub_release_notes_title_rc(self):
        release = Release.objects.create(version="6.2rc1")
        result = stub_release_notes_title(release)
        expected = (
            "===========================\n"
            "Django 6.2rc1 release notes\n"
            "==========================="
        )
        self.assertEqual(result, expected)


class FormatReleaseForCveTestCase(TestCase):
    def test_format_release_for_cve_final(self):
        release = Release.objects.create(version="4.1.8")
        result = format_release_for_cve(release)
        self.assertEqual(result, "4.1 before 4.1.8")

    def test_format_release_for_cve_high_micro(self):
        release = Release.objects.create(version="3.2.15")
        result = format_release_for_cve(release)
        self.assertEqual(result, "3.2 before 3.2.15")


class FormatReleasesForCvesTestCase(TestCase):
    def test_format_releases_for_cves_multiple(self):
        r1 = Release.objects.create(version="4.2.31")
        r2 = Release.objects.create(version="5.2.2")
        r3 = Release.objects.create(version="6.1.3")

        result = format_releases_for_cves([r1, r2, r3])
        self.assertEqual(
            result, "4.2 before 4.2.31, 5.2 before 5.2.2, and 6.1 before 6.1.3"
        )

    def test_format_releases_for_cves_single(self):
        r1 = Release.objects.create(version="3.2.20")
        result = format_releases_for_cves([r1])
        self.assertEqual(result, "3.2 before 3.2.20")

    def test_format_releases_for_cves_filters_prereleases(self):
        """Pre-releases shouldn't be listed in CVE descriptions."""
        r1 = Release.objects.create(version="3.2.21")
        r2 = Release.objects.create(version="5.2a1")
        r3 = Release.objects.create(version="4.2.22")

        result = format_releases_for_cves([r1, r2, r3])
        self.assertEqual(result, "3.2 before 3.2.21 and 4.2 before 4.2.22")


class FormatVersionForBlogpostTestCase(TestCase):
    def test_format_version_for_blogpost(self):
        result = format_version_for_blogpost("5.2.3")
        self.assertEqual(
            result,
            "`Django 5.2.3 <https://docs.djangoproject.com/en/dev/releases/5.2.3/>`_",
        )

    def test_format_version_for_blogpost_dot_zero(self):
        result = format_version_for_blogpost("5.2")
        self.assertEqual(
            result,
            "`Django 5.2 <https://docs.djangoproject.com/en/dev/releases/5.2/>`_",
        )


class FormatVersionsForBlogpostTestCase(TestCase):
    def test_format_versions_for_blogpost_single(self):
        versions = ["5.2.3"]
        result = format_versions_for_blogpost(versions)
        self.assertEqual(result, format_version_for_blogpost("5.2.3"))

    def test_format_versions_for_blogpost_two(self):
        versions = ["5.2.3", "5.1.5"]
        result = format_versions_for_blogpost(versions)
        expected = "{} and {}".format(
            format_version_for_blogpost("5.2.3"),
            format_version_for_blogpost("5.1.5"),
        )
        self.assertEqual(result, expected)

    def test_format_versions_for_blogpost_multiple(self):
        """Generates RST hyperlinks with Oxford comma."""
        versions = ["5.2.3", "5.1.5", "4.2.8"]
        result = format_versions_for_blogpost(versions)
        expected = "{}, {}, and {}".format(
            format_version_for_blogpost("5.2.3"),
            format_version_for_blogpost("5.1.5"),
            format_version_for_blogpost("4.2.8"),
        )
        self.assertEqual(result, expected)


class NextReleaseDateTestCase(TestCase):
    def test_next_release_date_basic(self):
        base_date = date(2024, 1, 3)
        self.assertEqual(next_release_date(base_date), date(2024, 2, 2))

    def test_next_release_date_datetime(self):
        base_datetime = datetime(2024, 1, 2, 12, 0, 0)
        result = next_release_date(base_datetime)
        self.assertEqual(result, datetime(2024, 2, 1, 12, 0))

    def test_next_release_date_year_boundary(self):
        base_date = date(2024, 12, 2)
        self.assertEqual(next_release_date(base_date), date(2025, 1, 1))


class RstBackticksTestCase(TestCase):
    def test_rst_backticks_single(self):
        result = rst_backticks("Hello `world`")
        self.assertEqual(result, "Hello ``world``")

    def test_rst_backticks_multiple(self):
        result = rst_backticks("`code` and `more code`")
        self.assertEqual(result, "``code`` and ``more code``")

    def test_rst_backticks_none(self):
        result = rst_backticks("Hello world")
        self.assertEqual(result, "Hello world")

    def test_rst_backticks_empty(self):
        result = rst_backticks("")
        self.assertEqual(result, "")


class RstUnderlineForHeadlineTestCase(TestCase):
    def test_rst_underline_short(self):
        result = rst_underline_for_headline("Hi")
        self.assertEqual(result, "Hi\n==")

    def test_rst_underline_long(self):
        text = "Django 5.2.3 release notes"
        result = rst_underline_for_headline(text)
        self.assertEqual(result, text + "\n" + "=" * len(text))

    def test_rst_underline_empty(self):
        result = rst_underline_for_headline("")
        self.assertEqual(result, "\n")
