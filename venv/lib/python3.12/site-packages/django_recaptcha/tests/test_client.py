import uuid
from unittest.mock import MagicMock, patch

from django import forms
from django.test import TestCase, override_settings

from django_recaptcha import client, fields


class DefaultForm(forms.Form):
    captcha = fields.ReCaptchaField()


class TestClient(TestCase):
    @patch("django_recaptcha.client.recaptcha_request")
    def test_client_success(self, mocked_response):
        read_mock = MagicMock()
        read_mock.read.return_value = (
            b'{"success": true, "challenge_ts":'
            b'"2019-01-11T13:57:23Z", "hostname": "testkey.google.com"}'
        )
        mocked_response.return_value = read_mock
        uuid_hex = uuid.uuid4().hex
        response = client.submit(
            uuid_hex,
            "somekey",
            "0.0.0.0",
        )

        # Quick way to test method call without needing to worry about Python 2
        # dicts not being ordered by default.
        self.assertIn("secret=somekey", mocked_response.call_args.__str__())
        self.assertIn("response=%s" % uuid_hex, mocked_response.call_args.__str__())
        self.assertIn("remoteip=0.0.0.0", mocked_response.call_args.__str__())
        self.assertTrue(response.is_valid)

    @patch("django_recaptcha.client.recaptcha_request")
    def test_client_failure(self, mocked_response):
        read_mock = MagicMock()
        read_mock.read.return_value = (
            b'{"success": false, "error-codes":'
            b'["invalid-input-response", "invalid-input-secret"]}'
        )
        mocked_response.return_value = read_mock
        uuid_hex = uuid.uuid4().hex
        response = client.submit(
            uuid_hex,
            "somekey",
            "0.0.0.0",
        )

        # Quick way to test method call without needing to worry about Python 2
        # dicts not being ordered by default.
        self.assertIn("secret=somekey", mocked_response.call_args.__str__())
        self.assertIn("response=%s" % uuid_hex, mocked_response.call_args.__str__())
        self.assertIn("remoteip=0.0.0.0", mocked_response.call_args.__str__())
        self.assertFalse(response.is_valid)
        self.assertEqual(
            response.error_codes.sort(),
            ["invalid-input-response", "invalid-input-secret"].sort(),
        )

    @patch("django_recaptcha.client.Request")
    @patch("django_recaptcha.client.build_opener")
    def test_client_request(self, mocked_builder, mocked_request):
        mock_read = MagicMock()
        mock_read.read.return_value = (
            b'{"success": false, "error-codes":'
            b'["invalid-input-response", "invalid-input-secret"]}'
        )
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_read
        mocked_builder.return_value = mock_opener
        form_params = {"g-recaptcha-response": "PASSED"}
        form = DefaultForm(form_params)
        form.is_valid()

        # Quick way to test method call without needing to worry about Python 2
        # dicts not being ordered by default.
        self.assertIn("data=", mocked_request.call_args.__str__())
        self.assertIn("remoteip=None", mocked_request.call_args.__str__())
        self.assertIn("response=PASSED", mocked_request.call_args.__str__())
        self.assertIn("secret=privkey", mocked_request.call_args.__str__())
        self.assertIn("headers=", mocked_request.call_args.__str__())
        self.assertIn(
            "'Content-type': 'application/x-www-form-urlencoded'",
            mocked_request.call_args.__str__(),
        )
        self.assertIn(
            "'User-agent': 'reCAPTCHA Django'", mocked_request.call_args.__str__()
        )
        self.assertIn(
            "url='https://www.google.com/recaptcha/api/siteverify'",
            mocked_request.call_args.__str__(),
        )
        mock_opener.open.assert_called_with(mocked_request(), timeout=10)
        mocked_builder.assert_called_with()

    @patch("django_recaptcha.client.ProxyHandler")
    @patch("django_recaptcha.client.Request")
    @patch("django_recaptcha.client.build_opener")
    @override_settings(RECAPTCHA_PROXY={"http": "aaaa.com"})
    def test_client_request_with_proxy_builder(
        self, mocked_builder, mocked_request, mocked_handler
    ):
        mock_read = MagicMock()
        mock_read.read.return_value = (
            b'{"success": false, "error-codes":'
            b'["invalid-input-response", "invalid-input-secret"]}'
        )
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_read
        mocked_builder.return_value = mock_opener
        form_params = {"g-recaptcha-response": "PASSED"}
        form = DefaultForm(form_params)
        form.is_valid()

        # Quick way to test method call without needing to worry about Python 2
        # dicts not being ordered by default.
        self.assertIn("data=", mocked_request.call_args.__str__())
        self.assertIn("remoteip=None", mocked_request.call_args.__str__())
        self.assertIn("response=PASSED", mocked_request.call_args.__str__())
        self.assertIn("secret=privkey", mocked_request.call_args.__str__())
        self.assertIn("headers=", mocked_request.call_args.__str__())
        self.assertIn(
            "'Content-type': 'application/x-www-form-urlencoded'",
            mocked_request.call_args.__str__(),
        )
        self.assertIn(
            "'User-agent': 'reCAPTCHA Django'", mocked_request.call_args.__str__()
        )
        self.assertIn(
            "url='https://www.google.com/recaptcha/api/siteverify'",
            mocked_request.call_args.__str__(),
        )
        mock_opener.open.assert_called_with(mocked_request(), timeout=10)
        mocked_handler.assert_called_with({"http": "aaaa.com"})
        mocked_builder.assert_called_with(mocked_handler())
