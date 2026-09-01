from unittest import skipIf

import requests
from django.conf import settings
from django.core import mail
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings

from djangoproject.tests import ReleaseMixin, patch_captcha

from .views import FoundationContactForm


def check_network_connection():
    try:
        requests.get("https://djangoproject.com")
    except requests.exceptions.ConnectionError:
        return False
    return True


has_network_connection = check_network_connection()


@override_settings(AKISMET_TESTING=True)
class ContactFormTests(ReleaseMixin, TestCase):
    def setUp(self):
        self.url = "/contact/foundation/"

    @override_settings(AKISMET_API_KEY="")  # Disable Akismet in tests
    def test_invalid_email(self):
        response = self.client.post(
            self.url,
            {
                "name": "A. Random Hacker",
                "email": "xxx",
                "message_subject": "Hello",
                "body": "Hello, World!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", ["Enter a valid email address."]
        )

    @override_settings(AKISMET_API_KEY="")  # Disable Akismet in tests
    def test_without_akismet(self):
        with patch_captcha():
            response = self.client.post(
                self.url,
                {
                    "name": "A. Random Hacker",
                    "email": "a.random@example.com",
                    "message_subject": "Hello",
                    "body": "Hello, World!",
                    "captcha": "TESTING",
                },
            )
        self.assertRedirects(response, "/contact/sent/")
        self.assertEqual(mail.outbox[-1].subject, "[Contact form] Hello")

    @skipIf(not has_network_connection, "Requires a network connection")
    def test_empty_name(self):
        response = self.client.post(
            self.url,
            {
                "name": "",
                "email": "a.random@example.com",
                "message_subject": "Hello",
                "body": "Hello, World!",
            },
        )
        self.assertFormError(
            response.context["form"], "name", ["This field is required."]
        )

    @skipIf(not has_network_connection, "Requires a network connection")
    def test_akismet_detect_spam(self):
        response = self.client.post(
            self.url,
            {
                # according to akismet this should flag as spam
                "name": "viagra-test-123",
                "email": "a.random@example.com",
                "message_subject": "Hello",
                "body": "Hello, World!",
            },
        )
        self.assertContains(response, "Akismet thinks this message is spam")
        self.assertEqual(len(mail.outbox), 0)

    @skipIf(not has_network_connection, "Requires a network connection")
    def test_akismet_not_spam(self):
        with patch_captcha():
            response = self.client.post(
                self.url,
                {
                    "name": "administrator",
                    "email": "a.random@example.com",
                    "message_subject": "Hello",
                    "body": "Hello, World!",
                    "captcha": "TESTING",
                },
            )
        self.assertRedirects(response, "/contact/sent/")
        self.assertEqual(mail.outbox[-1].subject, "[Contact form] Hello")

    @skipIf(not has_network_connection, "Requires a network connection")
    def test_captcha_token_required(self):
        form = FoundationContactForm(
            data={
                "name": "administrator",
                "email": "a.random@example.com",
                "message_subject": "Hello",
                "body": "Hello, World!",
            },
            request=HttpRequest(),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)


class BannerSponsorshipTests(ReleaseMixin, TestCase):
    @override_settings(AKISMET_API_KEY="")  # Disable Akismet in tests
    def test_failed_captcha_error_is_visible(self):
        with patch_captcha(is_valid=False):
            response = self.client.post(
                "/sponsor/banner/",
                {
                    "name": "A. Random Sponsor",
                    "email": "sponsor@example.com",
                    "message_subject": "monthly",
                    "body": "October, please.",
                    "captcha": "TESTING",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Error verifying reCAPTCHA")

    @override_settings(AKISMET_API_KEY="")  # Disable Akismet in tests
    def test_sponsor_banner_page(self):
        with patch_captcha():
            response = self.client.post(
                "/sponsor/banner/",
                {
                    "name": "A. Random Sponsor",
                    "email": "sponsor@example.com",
                    "message_subject": "monthly",
                    "body": "October, please.",
                    "captcha": "TESTING",
                },
            )
        self.assertRedirects(response, "/contact/sent/")
        msg = mail.outbox[-1]
        self.assertEqual(msg.subject, "[Banner sponsorship] One month: $10,000")
        self.assertEqual(
            msg.to,
            [
                settings.FUNDRAISING_DEFAULT_FROM_EMAIL,
                "treasurer@djangoproject.com",
                "dsf-board@googlegroups.com",
            ],
        )

    # The radio buttons render in the order of the choices of the field.
    RADIO_IDS = {"monthly": "id_message_subject_0", "weekly": "id_message_subject_1"}

    def assertLevelChecked(self, response, level):
        self.assertContains(response, f'id="{self.RADIO_IDS[level]}" checked')
        for other, radio_id in self.RADIO_IDS.items():
            if other != level:
                self.assertNotContains(response, f'id="{radio_id}" checked')

    def test_level_query_parameter_selects_the_radio_button(self):
        for level in self.RADIO_IDS:
            with self.subTest(level=level):
                response = self.client.get("/sponsor/banner/", {"level": level})
                self.assertEqual(
                    response.context["form"].initial["message_subject"], level
                )
                self.assertLevelChecked(response, level)

    def test_unknown_level_falls_back_to_the_default(self):
        for level in ["yearly", "", "monthly; DROP TABLE"]:
            with self.subTest(level=level):
                response = self.client.get("/sponsor/banner/", {"level": level})
                self.assertNotIn("message_subject", response.context["form"].initial)
                self.assertLevelChecked(response, "monthly")

    def test_the_page_links_to_both_levels(self):
        response = self.client.get("/sponsor/banner/")
        self.assertContains(response, 'href="?level=monthly#contact"')
        self.assertContains(response, 'href="?level=weekly#contact"')
        self.assertLevelChecked(response, "monthly")
