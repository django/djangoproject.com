"""
Helper code for obtaining an Akismet API client.

"""

# SPDX-License-Identifier: BSD-3-Clause

import textwrap
import warnings

import akismet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_AKISMET_CLIENT = None


def _client_from_settings(client_class):
    """
    Attempt to obtain an Akismet client from legacy configuration in Django
    settings.

    """
    key = getattr(settings, "AKISMET_API_KEY", None)  # noqa: B009
    url = getattr(settings, "AKISMET_BLOG_URL", None)  # noqa: B009
    if not all([key, url]):
        return None
    warnings.warn(
        textwrap.dedent(
            """
            Specifying Akismet configuration via the Django settings AKISMET_API_KEY and
            AKISMET_BLOG_URL is deprecated and support for it will be removed in a
            future version of django-contact-form.

            Please migrate to specifying the configuration in the environment variables
            PYTHON_AKISMET_API_KEY and PYTHON_AKISMET_BLOG_URL. Or, if you cannot
            configure via environment variables, write a subclass of
            `AkismetContactForm` and override its `get_akismet_client()` method to
            construct your Akismet client.
            """
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    client = client_class(config=akismet.Config(key, url))
    if client.verify_key(key, url):
        return client
    raise ImproperlyConfigured(
        "The Akismet configuration specified in your Django settings is invalid."
    )


def _client_from_environment(client_class):
    """
    Attempt to obtain an Akismet client from configuration in environment variables.

    """
    try:
        return client_class.validated_client()
    except akismet.ConfigurationError as exc:
        raise ImproperlyConfigured(
            "The Akismet configuration specified in your environment variables is "
            "missing or invalid."
        ) from exc


def _try_get_akismet_client(  # pylint: disable=inconsistent-return-statements
    client_class=akismet.SyncClient,
):
    """
    Attempt to obtain and return an instance of the given Akismet API client class..

    :raises django.core.exceptions.ImproperlyConfigured: When the Akismet client
       configuration is missing or invalid.

    """
    global _AKISMET_CLIENT  # pylint: disable=global-statement

    if _AKISMET_CLIENT is None:  # pragma: no branch
        for attempt in [  # pragma: no branch
            _client_from_settings,
            _client_from_environment,
        ]:
            _AKISMET_CLIENT = attempt(client_class)
            if _AKISMET_CLIENT is not None:
                return _AKISMET_CLIENT
    return _AKISMET_CLIENT


def _clear_cached_instance():
    """
    Clear the cached Akismet API client instance, so that it will be re-created the
    next time it is requested.

    """
    global _AKISMET_CLIENT  # pylint: disable=global-statement
    _AKISMET_CLIENT = None
