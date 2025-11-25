import uuid
import warnings
from urllib.parse import urlencode

from django.conf import settings
from django.forms import widgets

from django_recaptcha.constants import DEFAULT_RECAPTCHA_DOMAIN


class ReCaptchaBase(widgets.Widget):
    """
    Base widget to be used for Google ReCAPTCHA.

    public_key -- String value: can optionally be passed to not make use of the
        project wide Google Site Key.
    """

    recaptcha_response_name = "g-recaptcha-response"

    def __init__(self, api_params=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex
        self.api_params = api_params or {}

        self.attrs.setdefault("class", "g-recaptcha")
        if not "g-recaptcha" in self.attrs["class"]:
            self.attrs["class"] = "g-recaptcha " + self.attrs["class"]

    def value_from_datadict(self, data, files, name):
        return data.get(self.recaptcha_response_name, None)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        params = urlencode(self.api_params)
        context.update(
            {
                "public_key": self.attrs["data-sitekey"],
                "widget_uuid": self.uuid,
                "api_params": params,
                "recaptcha_domain": getattr(
                    settings, "RECAPTCHA_DOMAIN", DEFAULT_RECAPTCHA_DOMAIN
                ),
            }
        )
        return context

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["data-widget-uuid"] = self.uuid

        # Support the ability to override some of the Google data attrs.
        attrs["data-callback"] = base_attrs.get(
            "data-callback", "onSubmit_%s" % self.uuid
        )
        attrs["data-size"] = base_attrs.get("data-size", "normal")
        return attrs


class ReCaptchaV2Checkbox(ReCaptchaBase):
    input_type = "hidden"
    template_name = "django_recaptcha/widget_v2_checkbox.html"


class ReCaptchaV2Invisible(ReCaptchaBase):
    input_type = "hidden"
    template_name = "django_recaptcha/widget_v2_invisible.html"

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)

        # Invisible reCAPTCHA should not have another size
        attrs["data-size"] = "invisible"
        return attrs


class ReCaptchaV3(ReCaptchaBase):
    input_type = "hidden"
    template_name = "django_recaptcha/widget_v3.html"

    def __init__(
        self, api_params=None, action=None, required_score=None, *args, **kwargs
    ):
        super().__init__(api_params=api_params, *args, **kwargs)
        self.required_score = required_score or getattr(
            settings, "RECAPTCHA_REQUIRED_SCORE", None
        )

        # DeprecationWarning: remove this backwards compatibility code in the next major release.
        if self.attrs.get("required_score", None):
            warnings.warn(
                "The required_score attribute is deprecated. Please pass `required_score` as an argument directly to the widget, not as part of `attrs`.",
                DeprecationWarning,
                stacklevel=2,
            )

            # Populate required_score from widget attributes for backwards compatibility.
            self.required_score = self.attrs["required_score"]

        self.action = action

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        return attrs

    def value_from_datadict(self, data, files, name):
        return data.get(name)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update({"action": self.action})
        return context
