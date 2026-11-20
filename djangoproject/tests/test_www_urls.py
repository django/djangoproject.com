from django.test import TestCase


class IndividualMembershipNominationRedirectTests(TestCase):
    def test_individual_membership_nomination_redirect_exists(self):
        response = self.client.get("/foundation/individual-membership-nomination/")
        self.assertEqual(response.status_code, 302)


class NormalizeSlashesMiddlewareTests(TestCase):
    def test_double_slash_redirects_to_single_slash(self):
        response = self.client.get(
            "/community//",
            follow=False,
            headers={"host": "www.djangoproject.localhost"},
        )

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/community/")

    def test_triple_slash_redirects(self):
        response = self.client.get(
            "/community///",
            follow=False,
            headers={"host": "www.djangoproject.localhost"},
        )

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/community/")

    def test_normal_url_no_redirect(self):
        response = self.client.get(
            "/community/",
            follow=False,
            headers={"host": "www.djangoproject.localhost"},
        )

        self.assertEqual(response.status_code, 200)

    def test_invalid_normalized_path_no_redirect(self):
        response = self.client.get(
            "/nonexistent//page/",
            follow=False,
            headers={"host": "www.djangoproject.localhost"},
        )

        self.assertNotEqual(response.status_code, 301)


class ClipboardAccessibilityTests(TestCase):
    def test_clipboard_strings_node_present(self):
        response = self.client.get(
            "/",
            headers={"host": "www.djangoproject.localhost"},
        )
        self.assertContains(response, 'id="clipboard-strings"')
        self.assertContains(response, '<span id="clipboard-strings" hidden')
        self.assertContains(response, 'data-label-copy="Copy this code"')
        self.assertContains(response, 'data-label-copied="Copied!"')
        self.assertContains(response, 'data-label-error="Could not copy!"')

    def test_aria_live_status_region_present(self):
        response = self.client.get(
            "/",
            headers={"host": "www.djangoproject.localhost"},
        )
        self.assertContains(response, 'id="clipboard-status"')
        self.assertContains(response, 'role="status"')
        self.assertContains(response, 'aria-live="polite"')

