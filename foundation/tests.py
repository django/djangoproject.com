from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import TestCase


class MeetingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
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
