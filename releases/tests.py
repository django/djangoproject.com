from django.contrib.redirects.models import Redirect
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Release, create_releases_up_to_1_5
from .templatetags.release_notes import get_latest_micro_release


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


class TestDownloadsView(TestCase):
    url = reverse('download')

    def test_lts_overlap(self):
        Release.objects.create(major=1, minor=8, micro=0, is_lts=True, version='1.4')
        Release.objects.create(major=1, minor=6, micro=0, version='1.6')
        Release.objects.create(major=1, minor=7, micro=0, version='1.7')
        Release.objects.create(major=1, minor=8, micro=0, is_lts=True, version='1.8')

        response = self.client.get(self.url)
        self.assertEqual(response.context['current_version'], '1.8')
        self.assertEqual(response.context['previous_version'], '1.7')
        # Previous LTS (still supported)
        self.assertEqual(response.context['lts_version'], '1.4')
        # No longer supported versions
        self.assertEqual(response.context['earlier_versions'], ['1.6'])


class TestTemplateTags(TestCase):
    def test_get_latest_micro_release(self):
        Release.objects.create(major=1, minor=8, micro=0, is_lts=True, version='1.8')
        Release.objects.create(major=1, minor=8, micro=1, is_lts=True, version='1.8.1')

        self.assertEqual(get_latest_micro_release('1.8'), '1.8.1')
        self.assertEqual(get_latest_micro_release('1.4'), None)
