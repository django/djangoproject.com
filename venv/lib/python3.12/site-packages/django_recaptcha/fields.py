import logging
import sys
from urllib.error import HTTPError

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

from django_recaptcha import client
from django_recaptcha.constants import TEST_PRIVATE_KEY, TEST_PUBLIC_KEY
from django_recaptcha.widgets import ReCaptchaBase, ReCaptchaV2Checkbox, ReCaptchaV3

logger = logging.getLogger(__name__)


class ReCaptchaField(forms.CharField):
    widget = ReCaptchaV2Checkbox
    default_error_messages = {
        "captcha_invalid": _("Error verifying reCAPTCHA, please try again."),
        "captcha_error": _("Error verifying reCAPTCHA, please try again."),
    }

    def __init__(self, public_key=None, private_key=None, *args, **kwargs):
        """
        ReCaptchaField can accepts attributes which is a dictionary of
        attributes to be passed to the ReCaptcha widget class. The widget will
        loop over any options added and create the RecaptchaOptions
        JavaScript variables as specified in
        https://developers.google.com/recaptcha/docs/display#render_param
        """
        super().__init__(*args, **kwargs)

        if not isinstance(self.widget, ReCaptchaBase):
            raise ImproperlyConfigured(
                "django_recaptcha.fields.ReCaptchaField.widget"
                " must be a subclass of django_recaptcha.widgets.ReCaptchaBase"
            )

        # reCAPTCHA fields are always required.
        self.required = True

        # Setup instance variables.
        self.private_key = private_key or getattr(
            settings, "RECAPTCHA_PRIVATE_KEY", TEST_PRIVATE_KEY
        )
        self.public_key = public_key or getattr(
            settings, "RECAPTCHA_PUBLIC_KEY", TEST_PUBLIC_KEY
        )

        # Update widget attrs with data-sitekey.
        self.widget.attrs["data-sitekey"] = self.public_key

    def get_remote_ip(self):
        f = sys._getframe()
        while f:
            request = f.f_locals.get("request")
            if request:
                remote_ip = request.META.get("REMOTE_ADDR", "")
                forwarded_ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
                ip = remote_ip if not forwarded_ip else forwarded_ip
                return ip
            f = f.f_back

    def validate(self, value):
        super().validate(value)

        try:
            check_captcha = client.submit(
                recaptcha_response=value,
                private_key=self.private_key,
                remoteip=self.get_remote_ip(),
            )

        except HTTPError:  # Catch timeouts, etc
            raise ValidationError(
                self.error_messages["captcha_error"], code="captcha_error"
            )

        if not check_captcha.is_valid:
            logger.warning(
                "ReCAPTCHA validation failed due to: %s" % check_captcha.error_codes
            )
            raise ValidationError(
                self.error_messages["captcha_invalid"], code="captcha_invalid"
            )

        if (
            isinstance(self.widget, ReCaptchaV3)
            and check_captcha.action != self.widget.action
        ):
            logger.warning(
                "ReCAPTCHA validation failed due to: mismatched action. Expected '%s' but received '%s' from captcha server."
                % (self.widget.action, check_captcha.action)
            )
            raise ValidationError(
                self.error_messages["captcha_invalid"], code="captcha_invalid"
            )

        required_score = getattr(self.widget, "required_score", None)
        if required_score:
            # Our score values need to be floats, as that is the expected
            # response from the Google endpoint. Rather than ensure that on
            # the widget, we do it on the field to better support user
            # subclassing of the widgets.
            required_score = float(required_score)

            # If a score was expected but non was returned, default to a 0,
            # which is the lowest score that it can return. This is to do our
            # best to assure a failure here, we can not assume that a form
            # that needed the threshold should be valid if we didn't get a
            # value back.
            score = float(check_captcha.extra_data.get("score", 0))

            if required_score > score:
                logger.warning(
                    "ReCAPTCHA validation failed due to its score of %s"
                    " being lower than the required amount." % score
                )
                raise ValidationError(
                    self.error_messages["captcha_invalid"], code="captcha_invalid"
                )
