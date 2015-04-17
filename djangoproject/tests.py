from django.test import TestCase
from django_hosts.resolvers import reverse


class TemplateViewTests(TestCase):
    """
    Tests for views that are instances of TemplateView.
    """

    def assertView(self, name):
        self.assertContains(self.client.get(reverse(name, host='www')), 'django')

    def test_homepage(self):
        self.assertView('homepage')

    def test_overview(self):
        self.assertView('overview')

    def test_start(self):
        self.assertView('start')

    def test_code_of_conduct(self):
        self.assertView('code_of_conduct')

    def test_conduct_faq(self):
        self.assertView('conduct_faq')

    def test_conduct_reporting(self):
        self.assertView('conduct_reporting')

    def test_conduct_enforcement(self):
        self.assertView('conduct_enforcement')

    def test_conduct_changes(self):
        self.assertView('conduct_changes')

    def test_styleguide(self):
        self.assertView('styleguide')
