from django.test import SimpleTestCase
from django.urls import reverse


class AboutRedirectTests(SimpleTestCase):
    def test_about_redirects_to_foundation(self):
        response = self.client.get("/about/")
        self.assertRedirects(
            response,
            reverse("members:developer-members"),
            status_code=301,
        )
