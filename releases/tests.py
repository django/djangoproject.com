from __future__ import unicode_literals

from django.contrib.redirects.models import Redirect
from django.test import TestCase

from .models import create_releases_up_to_1_5


class LegacyURLsTests(TestCase):

    fixtures = ['redirects-downloads']          # provided by the legacy app

    def test_legacy_redirects(self):
        # Save list of redirects, then wipe them
        redirects = list(Redirect.objects.values_list('old_path', 'new_path'))
        Redirect.objects.all().delete()
        # Ensure the releases app faithfully reproduces the redirects
        create_releases_up_to_1_5()
        for old_path, new_path in redirects:
            response = self.client.get(old_path, follow=False)
            location = response.get('Location', '')
            if location.startswith('http://testserver'):
                location = location[17:]
            self.assertEquals(location, new_path)
            self.assertEquals(response.status_code, 301)
