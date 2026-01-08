from django.test import TestCase


class IndividualMembershipNominationRedirectTests(TestCase):
    def test_individual_membership_nomination_redirect_exists(self):
        response = self.client.get(
            "/foundation/individual-membership-nomination/"
        )
        self.assertEqual(response.status_code, 302)
