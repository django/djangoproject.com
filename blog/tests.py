from contextlib import redirect_stderr
from datetime import date, timedelta
from io import StringIO

import time_machine
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, translation

from .models import ContentFormat, Entry, Event, ImageUpload
from .sitemaps import WeblogSitemap


class DateTimeMixin:
    def setUp(self):
        self.now = timezone.now()
        self.yesterday = self.now - timedelta(days=1)
        self.tomorrow = self.now + timedelta(days=1)


class EntryTestCase(DateTimeMixin, TestCase):
    def test_manager_active(self):
        """
        Make sure that the Entry manager's `active` method works
        """
        Entry.objects.create(
            pub_date=self.now, is_active=False, headline="inactive", slug="a"
        )
        Entry.objects.create(
            pub_date=self.now, is_active=True, headline="active", slug="b"
        )

        self.assertQuerySetEqual(
            Entry.objects.published(),
            ["active"],
            transform=lambda entry: entry.headline,
        )

    def test_manager_published(self):
        """
        Make sure that the Entry manager's `published` method works
        """
        Entry.objects.create(
            pub_date=self.yesterday, is_active=False, headline="past inactive", slug="a"
        )
        Entry.objects.create(
            pub_date=self.yesterday, is_active=True, headline="past active", slug="b"
        )
        Entry.objects.create(
            pub_date=self.tomorrow,
            is_active=False,
            headline="future inactive",
            slug="c",
        )
        Entry.objects.create(
            pub_date=self.tomorrow, is_active=True, headline="future active", slug="d"
        )

        self.assertQuerySetEqual(
            Entry.objects.published(),
            ["past active"],
            transform=lambda entry: entry.headline,
        )

    def test_docutils_safe(self):
        """
        Make sure docutils' file inclusion directives are disabled by default.
        """
        with redirect_stderr(StringIO()):
            entry = Entry.objects.create(
                pub_date=self.now,
                is_active=True,
                headline="active",
                content_format="reST",
                body=".. raw:: html\n    :file: somefile\n",
                slug="a",
            )
        self.assertIn("<p>&quot;raw&quot; directive disabled.</p>", entry.body_html)
        self.assertIn(".. raw:: html\n    :file: somefile", entry.body_html)

    def test_content_format_html(self):
        entry = Entry.objects.create(
            pub_date=self.now,
            slug="a",
            body="<strong>test</strong>",
            content_format=ContentFormat.HTML,
        )
        self.assertHTMLEqual(entry.body_html, "<strong>test</strong>")

    def test_content_format_reST(self):
        entry = Entry.objects.create(
            pub_date=self.now,
            slug="a",
            body="**test**",
            content_format=ContentFormat.REST,
        )
        self.assertHTMLEqual(entry.body_html, "<p><strong>test</strong></p>")

    def test_content_format_markdown(self):
        entry = Entry.objects.create(
            pub_date=self.now,
            slug="a",
            body="**test**",
            content_format=ContentFormat.MARKDOWN,
        )
        self.assertHTMLEqual(entry.body_html, "<p><strong>test</strong></p>")

    def test_header_base_level_reST(self):
        entry = Entry.objects.create(
            pub_date=self.now,
            slug="a",
            body="test\n====",
            content_format=ContentFormat.REST,
        )
        self.assertHTMLEqual(
            entry.body_html, '<div class="section" id="s-test"><h3>test</h3></div>'
        )

    def test_header_base_level_markdown(self):
        entry = Entry.objects.create(
            pub_date=self.now,
            slug="a",
            body="# test",
            content_format=ContentFormat.MARKDOWN,
        )
        self.assertHTMLEqual(entry.body_html, '<h3 id="s-test">test</h3>')

    def test_pub_date_localized(self):
        entry = Entry(pub_date=date(2005, 7, 21))
        self.assertEqual(entry.pub_date_localized, "July 21, 2005")
        with translation.override("nn"):
            self.assertEqual(entry.pub_date_localized, "21. juli 2005")


class EventTestCase(DateTimeMixin, TestCase):
    def test_manager_past_future(self):
        """
        Make sure that the Event manager's `past` and `future` methods works
        """
        Event.objects.create(date=self.yesterday, pub_date=self.now, headline="past")
        Event.objects.create(date=self.tomorrow, pub_date=self.now, headline="future")

        self.assertQuerySetEqual(
            Event.objects.future(), ["future"], transform=lambda event: event.headline
        )
        self.assertQuerySetEqual(
            Event.objects.past(), ["past"], transform=lambda event: event.headline
        )

    def test_manager_past_future_include_today(self):
        """
        Make sure that both .future() and .past() include today's events.
        """
        Event.objects.create(date=self.now, pub_date=self.now, headline="today")

        self.assertQuerySetEqual(
            Event.objects.future(), ["today"], transform=lambda event: event.headline
        )
        self.assertQuerySetEqual(
            Event.objects.past(), ["today"], transform=lambda event: event.headline
        )

    def test_past_future_ordering(self):
        """
        Make sure the that .future() and .past() use the actual date for ordering
        (and not the pub_date).
        """
        D = timedelta(days=1)
        Event.objects.create(
            date=self.yesterday - D, pub_date=self.yesterday - D, headline="a"
        )
        Event.objects.create(date=self.yesterday, pub_date=self.yesterday, headline="b")

        Event.objects.create(date=self.tomorrow, pub_date=self.tomorrow, headline="c")
        Event.objects.create(
            date=self.tomorrow + D, pub_date=self.tomorrow + D, headline="d"
        )

        self.assertQuerySetEqual(
            Event.objects.future(), ["c", "d"], transform=lambda event: event.headline
        )
        self.assertQuerySetEqual(
            Event.objects.past(), ["b", "a"], transform=lambda event: event.headline
        )


class ViewsTestCase(DateTimeMixin, TestCase):
    def test_staff_with_change_permission_can_see_unpublished_detail_view(self):
        """
        Staff users with change permission on BlogEntry can't see unpublished entries
        in the list, but can view the detail page
        """
        e1 = Entry.objects.create(
            pub_date=self.yesterday, is_active=False, headline="inactive", slug="a"
        )
        user = User.objects.create(username="staff", is_staff=True)
        # Add blog entry change permission

        content_type = ContentType.objects.get_for_model(Entry)
        change_permission = Permission.objects.get(
            content_type=content_type, codename="change_entry"
        )
        user.user_permissions.add(change_permission)
        self.client.force_login(user)
        self.assertEqual(Entry.objects.all().count(), 1)
        response = self.client.get(reverse("weblog:index"))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            reverse(
                "weblog:entry",
                kwargs={
                    "year": e1.pub_date.year,
                    "month": e1.pub_date.strftime("%b").lower(),
                    "day": e1.pub_date.day,
                    "slug": e1.slug,
                },
            )
        )
        request = response.context["request"]
        self.assertTrue(request.user.is_staff)
        self.assertTrue(request.user.has_perm("blog.change_entry"))
        self.assertEqual(response.status_code, 200)

    def test_staff_without_change_permission_cannot_see_unpublished_detail_view(self):
        """
        Staff users without change permission on BlogEntry can't see unpublished entries
        """
        e1 = Entry.objects.create(
            pub_date=self.yesterday, is_active=False, headline="inactive", slug="a"
        )
        user = User.objects.create(username="staff-no-perm", is_staff=True)
        # No permissions added
        self.client.force_login(user)
        self.assertEqual(Entry.objects.all().count(), 1)

        # Test detail view for unpublished entry - should return 404
        response = self.client.get(
            reverse(
                "weblog:entry",
                kwargs={
                    "year": e1.pub_date.year,
                    "month": e1.pub_date.strftime("%b").lower(),
                    "day": e1.pub_date.day,
                    "slug": e1.slug,
                },
            )
        )
        request = response.context["request"]
        self.assertTrue(request.user.is_staff)
        self.assertFalse(request.user.has_perm("blog.change_entry"))
        self.assertEqual(response.status_code, 404)

    def test_no_past_upcoming_events(self):
        """
        Make sure there are no past event in the "upcoming events" sidebar (#399)
        """
        # We need a published entry on the index page so that it doesn't return a 404
        Entry.objects.create(pub_date=self.yesterday, is_active=True, slug="a")
        Event.objects.create(
            date=self.yesterday, pub_date=self.now, is_active=True, headline="Jezdezcon"
        )
        response = self.client.get(reverse("weblog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["events"], [])

    def test_no_unpublished_future_events(self):
        """
        Make sure there are no unpublished future events in the "upcoming events" sidebar
        """
        # We need a published entry on the index page so that it doesn't return a 404
        Entry.objects.create(pub_date=self.yesterday, is_active=True, slug="a")
        Event.objects.create(
            date=self.tomorrow,
            pub_date=self.yesterday,
            is_active=False,
            headline="inactive",
        )
        Event.objects.create(
            date=self.tomorrow,
            pub_date=self.tomorrow,
            is_active=True,
            headline="future publish date",
        )

        for user in [
            None,
            User.objects.create(username="non-staff", is_staff=False),
            User.objects.create(username="staff", is_staff=True),
            User.objects.create_superuser(username="superuser"),
        ]:
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse("weblog:index"))
            with self.subTest(user=user):
                self.assertEqual(response.status_code, 200)
                self.assertQuerySetEqual(response.context["events"], [])

    def test_anonymous_user_cannot_see_unpublished_entries(self):
        """
        Anonymous users can't see unpublished entries at all (list or detail view)
        """
        # Create a published entry to ensure the list view works
        published_entry = Entry.objects.create(
            pub_date=self.yesterday,
            is_active=True,
            headline="published",
            slug="published",
        )

        # Create an unpublished entry
        unpublished_entry = Entry.objects.create(
            pub_date=self.tomorrow,
            is_active=True,
            headline="unpublished",
            slug="unpublished",
        )

        # Test list view - should return 200 but not include the unpublished entry
        response = self.client.get(reverse("weblog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "published")
        self.assertNotContains(response, "unpublished")

        # Test detail view for unpublished entry - should return 404
        unpublished_url = reverse(
            "weblog:entry",
            kwargs={
                "year": unpublished_entry.pub_date.year,
                "month": unpublished_entry.pub_date.strftime("%b").lower(),
                "day": unpublished_entry.pub_date.day,
                "slug": unpublished_entry.slug,
            },
        )
        response = self.client.get(unpublished_url)
        self.assertEqual(response.status_code, 404)

        # Test detail view for published entry - should return 200
        published_url = reverse(
            "weblog:entry",
            kwargs={
                "year": published_entry.pub_date.year,
                "month": published_entry.pub_date.strftime("%b").lower(),
                "day": published_entry.pub_date.day,
                "slug": published_entry.slug,
            },
        )
        response = self.client.get(published_url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_see_unpublished_entries(self):
        """
        Non-staff users can't see unpublished entries at all (list or detail view)
        """
        user = User.objects.create(username="non-staff", is_staff=False)
        self.client.force_login(user)

        # Create a published entry to ensure the list view works
        published_entry = Entry.objects.create(
            pub_date=self.yesterday,
            is_active=True,
            headline="published",
            slug="published",
        )

        # Create an unpublished entry
        unpublished_entry = Entry.objects.create(
            pub_date=self.tomorrow,
            is_active=True,
            headline="unpublished",
            slug="unpublished",
        )

        # Test list view - should return 200 but not include the unpublished entry
        response = self.client.get(reverse("weblog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "published")
        self.assertNotContains(response, "unpublished")

        # Test detail view for unpublished entry - should return 404
        unpublished_url = reverse(
            "weblog:entry",
            kwargs={
                "year": unpublished_entry.pub_date.year,
                "month": unpublished_entry.pub_date.strftime("%b").lower(),
                "day": unpublished_entry.pub_date.day,
                "slug": unpublished_entry.slug,
            },
        )
        response = self.client.get(unpublished_url)
        self.assertEqual(response.status_code, 404)

        # Test detail view for published entry - should return 200
        published_url = reverse(
            "weblog:entry",
            kwargs={
                "year": published_entry.pub_date.year,
                "month": published_entry.pub_date.strftime("%b").lower(),
                "day": published_entry.pub_date.day,
                "slug": published_entry.slug,
            },
        )
        response = self.client.get(published_url)
        self.assertEqual(response.status_code, 200)


class SitemapTests(DateTimeMixin, TestCase):
    def test_sitemap(self):
        entry = Entry.objects.create(
            pub_date=self.yesterday, is_active=True, headline="foo", slug="foo"
        )
        sitemap = WeblogSitemap()
        urls = sitemap.get_urls()
        self.assertEqual(len(urls), 1)
        url_info = urls[0]
        self.assertEqual(url_info["location"], entry.get_absolute_url())


class ImageUploadTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser("test")

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_uploaded_by(self):
        # Can't test the ModelForm directly because the logic in
        # ModelAdmin.save_model()
        data = {
            "title": "test",
            "alt_text": "test",
            "image": ContentFile(b".", name="test.png"),
        }
        response = self.client.post(
            reverse("admin:blog_imageupload_add"),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        upload = ImageUpload.objects.get()
        self.assertEqual(upload.uploaded_by, self.user)

    def test_contentformat_image_tags(self):
        for cf, expected in [
            (ContentFormat.REST, ".. image:: /test/image.png\n   :alt: TEST"),
            (ContentFormat.HTML, '<img src="/test/image.png" alt="TEST">'),
            (ContentFormat.MARKDOWN, "![TEST](/test/image.png)"),
        ]:
            with self.subTest(contentformat=cf):
                self.assertEqual(
                    cf.img(url="/test/image.png", alt_text="TEST"),
                    expected,
                )

    @time_machine.travel("2005-07-21")
    def test_full_url(self):
        i = ImageUpload.objects.create(
            title="test",
            alt_text="test",
            image=ContentFile(b".", name="test.png"),
        )
        # Because the storage is persistent between test runs, running this
        # test twice will trigger a filename clash and the storage will append
        # a random suffix to the filename, hence the use of assertRegex here.
        self.assertRegex(
            i.full_url,
            r"http://www\.djangoproject\.localhost:8000"
            r"/m/blog/images/2005/07/test(_\w+)?\.png",
        )

    def test_alt_text_html_escape(self):
        testdata = [
            (ContentFormat.HTML, 'te"st', '<img src="." alt="te&quot;st">'),
            (ContentFormat.HTML, "te<st>", '<img src="." alt="te&lt;st&gt;">'),
            (ContentFormat.MARKDOWN, 'te"st', '<img src="." alt="te&quot;st">'),
            (ContentFormat.MARKDOWN, "te[st]", '<img src="." alt="te[st]">'),
            (ContentFormat.MARKDOWN, "te{st}", '<img src="." alt="te{st}">'),
            (ContentFormat.MARKDOWN, "te<st>", '<img src="." alt="te&lt;st&gt;">'),
            (ContentFormat.MARKDOWN, "test*", '<img src="." alt="test*">'),
            (ContentFormat.MARKDOWN, "test_", '<img src="." alt="test_">'),
            (ContentFormat.MARKDOWN, "test`", '<img src="." alt="test`">'),
            (ContentFormat.MARKDOWN, "test+", '<img src="." alt="test+">'),
            (ContentFormat.MARKDOWN, "test-", '<img src="." alt="test-">'),
            (ContentFormat.MARKDOWN, "test.", '<img src="." alt="test.">'),
            (ContentFormat.MARKDOWN, "test!", '<img src="." alt="test!">'),
            (ContentFormat.MARKDOWN, "te\nst", '<img src="." alt="te\nst">'),
            (ContentFormat.REST, 'te"st', '<img src="." alt="te&quot;st">'),
            (ContentFormat.REST, "te[st]", '<img src="." alt="te[st]">'),
            (ContentFormat.REST, "te{st}", '<img src="." alt="te{st}">'),
            (ContentFormat.REST, "te<st>", '<img src="." alt="te&lt;st&gt;">'),
            (ContentFormat.REST, "te:st", '<img src="." alt="te:st">'),
            (ContentFormat.REST, "test*", '<img src="." alt="test*">'),
            (ContentFormat.REST, "test_", '<img src="." alt="test_">'),
            (ContentFormat.REST, "test`", '<img src="." alt="test`">'),
            (ContentFormat.REST, "test+", '<img src="." alt="test+">'),
            (ContentFormat.REST, "test-", '<img src="." alt="test-">'),
            (ContentFormat.REST, "test.", '<img src="." alt="test.">'),
            (ContentFormat.REST, "test!", '<img src="." alt="test!">'),
        ]
        for cf, alt_text, expected in testdata:
            # RST doesn't like an empty src, so we use . instead
            img_tag = cf.img(url=".", alt_text=alt_text)
            if cf is ContentFormat.MARKDOWN:
                expected = f"<p>{expected}</p>"
            with self.subTest(cf=cf, alt_text=alt_text):
                self.assertHTMLEqual(
                    ContentFormat.to_html(cf, img_tag),
                    expected,
                )
