from unittest.mock import MagicMock, PropertyMock, patch
from urllib.error import HTTPError

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from django_recaptcha import fields, widgets
from django_recaptcha.client import RecaptchaResponse


class DefaultForm(forms.Form):
    captcha = fields.ReCaptchaField()


class TestFields(TestCase):
    @patch("django_recaptcha.fields.client.submit")
    def test_client_success_response(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        form_params = {"g-recaptcha-response": "PASSED"}
        form = DefaultForm(form_params)
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    def test_client_failure_response(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(
            is_valid=False, error_codes=["410"]
        )
        form_params = {"g-recaptcha-response": "PASSED"}
        form = DefaultForm(form_params)
        self.assertFalse(form.is_valid())

    def test_widget_check(self):
        with self.assertRaises(ImproperlyConfigured):

            class ImporperForm(forms.Form):
                captcha = fields.ReCaptchaField(widget=forms.Textarea)

    @patch("django_recaptcha.fields.client.submit")
    def test_field_instantiate_values(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        class NonDefaultForm(forms.Form):
            captcha = fields.ReCaptchaField(
                private_key="NewUpdatedKey", public_key="NewPubKey"
            )

        form_params = {"g-recaptcha-response": "PASSED"}
        form = NonDefaultForm(form_params)
        self.assertTrue(form.is_valid())
        mocked_submit.assert_called_with(
            private_key="NewUpdatedKey",
            recaptcha_response="PASSED",
            remoteip=None,
        )
        html = form.as_p()
        self.assertIn('data-sitekey="NewPubKey"', html)

    @patch("django_recaptcha.client.recaptcha_request")
    def test_field_captcha_errors(self, mocked_response):
        read_mock = MagicMock()
        read_mock.read.return_value = (
            b'{"success": false, "error-codes":'
            b'["invalid-input-response", "invalid-input-secret"]}'
        )
        mocked_response.return_value = read_mock
        form_params = {"g-recaptcha-response": "PASSED"}
        form = DefaultForm(form_params)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["captcha"], ["Error verifying reCAPTCHA, please try again."]
        )

        mocked_response.side_effect = HTTPError(
            url="https://www.google.com/recaptcha/api/siteverify",
            code=410,
            fp=None,
            msg="Oops",
            hdrs="",
        )
        form = DefaultForm(form_params)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["captcha"], ["Error verifying reCAPTCHA, please try again."]
        )


class TestWidgets(TestCase):
    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_default_v2_checkbox_html(self, mocked_uuid):
        test_hex = "928e8e017b114e1b9d3a3e877cfc5844"
        mocked_uuid.return_value = test_hex

        class DefaultCheckForm(forms.Form):
            captcha = fields.ReCaptchaField()

        form = DefaultCheckForm()
        html = form.as_p()
        # There should not be a label rendered for the checkbox. The ReCAPTCHA JS generates the label.
        self.assertNotIn("label", html)
        # Required is not a valid attribute as we aren't rendering a traditional input
        # Make sure it is not rendered in the HTML
        self.assertNotIn("required", html)
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js' '"></script>', html
        )
        self.assertIn('data-size="normal"', html)
        self.assertIn('class="g-recaptcha"', html)
        self.assertIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn("var onSubmit_%s = function(token) {" % test_hex, html)

    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_v2_checkbox_attribute_changes_html(self, mocked_uuid):
        test_hex = "e83ccae286ad4784bd47f7ddc40cfd6f"
        mocked_uuid.return_value = test_hex

        class CheckboxAttrForm(forms.Form):
            captcha = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV2Checkbox(
                    attrs={
                        "class": "custom-class",
                        "data-theme": "dark",
                        "data-callback": "customCallback",
                        "data-size": "compact",
                    },
                    api_params={"hl": "af"},
                )
            )

        form = CheckboxAttrForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js' '?hl=af"></script>',
            html,
        )
        # There should not be a label rendered for the checkbox. The ReCAPTCHA JS generates the label.
        self.assertNotIn("label", html)
        # Required is not a valid attribute as we aren't rendering a traditional input
        # Make sure it is not rendered in the HTML
        self.assertNotIn("required", html)
        self.assertIn('data-theme="dark"', html)
        self.assertNotIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('data-callback="customCallback"', html)
        self.assertIn('data-size="compact"', html)
        self.assertIn('class="g-recaptcha custom-class"', html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn("var onSubmit_%s = function(token) {" % test_hex, html)

    @override_settings(RECAPTCHA_DOMAIN="www.recaptcha.net")
    def test_default_v2_checkbox_domain_html(self):
        class DomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV2Checkbox())

        form = DomainForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.recaptcha.net/recaptcha/api.js">' "</script>",
            html,
        )

    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_default_v2_invisible_html(self, mocked_uuid):
        test_hex = "72f853eb8b7e4022b808be0f5c3bc297"
        mocked_uuid.return_value = test_hex

        class InvisForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV2Invisible())

        form = InvisForm()
        html = form.as_p()
        # Invisible captchas don't have labels
        self.assertNotIn("label", html)
        # Required is not a valid attribute as we aren't rendering a traditional input
        # Make sure it is not rendered in the HTML
        self.assertNotIn("required", html)
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js' '"></script>', html
        )
        self.assertIn('data-size="invisible"', html)
        self.assertIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('class="g-recaptcha"', html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn("var onSubmit_%s = function(token) {" % test_hex, html)
        self.assertIn("var verifyCaptcha_%s = function(e) {" % test_hex, html)
        self.assertIn('.g-recaptcha[data-widget-uuid="%s"]' % test_hex, html)

    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_v2_invisible_attribute_changes_html(self, mocked_uuid):
        test_hex = "8b220c54ddb849b8bb59bda5da57baea"
        mocked_uuid.return_value = test_hex

        class InvisAttrForm(forms.Form):
            captcha = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV2Invisible(
                    attrs={
                        "class": "custom-class",
                        "data-theme": "dark",
                        "data-callback": "customCallbackInvis",
                        "data-size": "compact",
                    },
                    api_params={"hl": "cl"},
                )
            )

        form = InvisAttrForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js' '?hl=cl"></script>',
            html,
        )
        self.assertNotIn('data-size="compact"', html)
        self.assertIn('data-size="invisible"', html)
        self.assertNotIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('data-callback="customCallbackInvis"', html)
        self.assertIn('class="g-recaptcha custom-class"', html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn("var onSubmit_%s = function(token) {" % test_hex, html)
        self.assertIn("var verifyCaptcha_%s = function(e) {" % test_hex, html)
        self.assertIn('.g-recaptcha[data-widget-uuid="%s"]' % test_hex, html)

    @override_settings(RECAPTCHA_DOMAIN="www.recaptcha.net")
    def test_default_v2_invisible_domain_html(self):
        class InvisDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV2Invisible())

        form = InvisDomainForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.recaptcha.net/recaptcha/api.js">' "</script>",
            html,
        )

    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_default_v3_html(self, mocked_uuid):
        test_hex = "c7a86421ca394661acccea374931d260"
        mocked_uuid.return_value = test_hex

        class InvisForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3())

        form = InvisForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js'
            '?render=pubkey"></script>',
            html,
        )
        # ReCaptcha V3 widget has input_type=hidden, there should be no label element in the html
        self.assertNotIn("label", html)
        # Required is not a valid attribute as we aren't rendering a traditional input
        # Make sure it is not rendered in the HTML
        self.assertNotIn("required", html)

        self.assertIn('data-size="normal"', html)
        self.assertIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('class="g-recaptcha"', html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn('.g-recaptcha[data-widget-uuid="%s"]' % test_hex, html)
        # By default, the action should NOT be in the JS code
        self.assertNotIn("action", html)

    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_default_v3_html_with_action(self, mocked_uuid):
        test_hex = "c7a86421ca394661acccea374931d260"
        mocked_uuid.return_value = test_hex

        class InvisForm(forms.Form):
            # We want to check that the action is passed to the JS code
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3(action="needle"))

        form = InvisForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js'
            '?render=pubkey"></script>',
            html,
        )
        # ReCaptcha V3 widget has input_type=hidden, there should be no label element in the html
        self.assertNotIn("label", html)
        # Required is not a valid attribute as we aren't rendering a traditional input
        # Make sure it is not rendered in the HTML
        self.assertNotIn("required", html)

        self.assertIn('data-size="normal"', html)
        self.assertIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('class="g-recaptcha"', html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn('.g-recaptcha[data-widget-uuid="%s"]' % test_hex, html)

        # Expect the action to be in the JS code
        self.assertIn("action: 'needle'", html)

    @patch("django_recaptcha.widgets.uuid.UUID.hex", new_callable=PropertyMock)
    def test_v3_attribute_changes_html(self, mocked_uuid):
        test_hex = "f367f89a797a4985acd986275b3df22f"
        mocked_uuid.return_value = test_hex

        class InvisAttrForm(forms.Form):
            captcha = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(
                    attrs={
                        "data-theme": "dark",
                        "data-callback": "customCallbackInvis",
                        "data-size": "compact",
                    },
                    api_params={"hl": "cl"},
                )
            )

        form = InvisAttrForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.google.com/recaptcha/api.js'
            '?render=pubkey&hl=cl"></script>',
            html,
        )
        self.assertIn('data-size="compact"', html)
        self.assertNotIn('data-callback="onSubmit_%s"' % test_hex, html)
        self.assertIn('data-callback="customCallbackInvis"', html)
        self.assertIn('class="g-recaptcha"', html)
        self.assertIn('data-widget-uuid="%s"' % test_hex, html)
        self.assertIn('data-sitekey="pubkey"', html)
        self.assertIn('.g-recaptcha[data-widget-uuid="%s"]' % test_hex, html)

    @override_settings(RECAPTCHA_DOMAIN="www.recaptcha.net")
    def test_default_v3_domain_html(self):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3())

        form = VThreeDomainForm()
        html = form.as_p()
        self.assertIn(
            '<script src="https://www.recaptcha.net/recaptcha/api.js'
            '?render=pubkey"></script>',
            html,
        )

    # TODO: DeprecationWarning: remove backwards compatibility test
    def test_field_required_score_attribute_html(self):
        with self.assertWarnsMessage(DeprecationWarning, "required_score"):

            class VThreeDomainForm(forms.Form):
                captcha = fields.ReCaptchaField(
                    # required_score is deprecated as an attribute
                    widget=widgets.ReCaptchaV3(attrs={"required_score": 0.8})
                )

    @patch("django_recaptcha.fields.client.submit")
    def test_client_success_response_v3(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(required_score=0.8)
            )

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0.9}
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    def test_client_failure_response_v3(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(
                widget=widgets.ReCaptchaV3(required_score=0.8)
            )

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0.1}
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertFalse(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    def test_client_empty_score_threshold_v3(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3())

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0.1}
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    def test_client_invalid_action_v3(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3(action="form"))

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0.1}, action="something_unexpected"
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertFalse(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    def test_client_valid_action_v3(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3(action="form"))

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0.1}, action="form"
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    @override_settings(RECAPTCHA_REQUIRED_SCORE=0.0)
    def test_required_score_human_setting(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3())

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0.85}
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    @override_settings(RECAPTCHA_REQUIRED_SCORE=0.85)
    def test_required_score_bot_setting(self, mocked_submit):
        class VThreeDomainForm(forms.Form):
            captcha = fields.ReCaptchaField(widget=widgets.ReCaptchaV3())

        mocked_submit.return_value = RecaptchaResponse(
            is_valid=True, extra_data={"score": 0}
        )
        form_params = {"captcha": "PASSED"}
        form = VThreeDomainForm(form_params)
        self.assertFalse(form.is_valid())
