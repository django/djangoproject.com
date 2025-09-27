from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse


class MeetingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        cls.site = Site.objects.get_current()

    def test_latest_meeting_minutes(self):
        page = FlatPage.objects.create(
            title="Foundation",
            url="/foundation/",
            template_name="flatpages/foundation.html",
        )
        page.sites.add(self.site)

        response = self.client.get("/foundation/")

        self.assertContains(response, "Latest DSF meeting minutes")
        self.assertContains(response, "https://github.com/django/dsf-minutes")

    def test_minutes_redirect(self):
        url = reverse(
            "minutes_redirect",
            kwargs={"year": 2025, "month": "Feb", "day": 13, "slug": "foo"},
        )
        response = self.client.get(url)
        self.assertRedirects(
            response,
            "https://github.com/django/dsf-minutes/blob/main/2025/2025-02-13.md",
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_minutes_redirect_not_found(self):
        url = reverse(
            "minutes_redirect",
            kwargs={"year": 2025, "month": "Jan", "day": 13, "slug": "foo"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
