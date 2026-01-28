from django.test import TestCase
from django_hosts.resolvers import reverse

class IndividualMembershipNominationRedirectTests(TestCase):
    def test_individual_membership_nomination_redirect_exists(self):
        response = self.client.get("/foundation/individual-membership-nomination/")
        self.assertEqual(response.status_code, 302)

class NormalizeSlashesMiddlewareTests(TestCase):
    def test_double_slash_redirects_to_single_slash(self):
        response = self.client.get(
            "/community//",
            follow=True,
            HTTP_HOST="www.djangoproject.localhost",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.request["PATH_INFO"].endswith("/community/"))