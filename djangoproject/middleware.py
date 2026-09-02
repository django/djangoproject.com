import re

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.middleware.locale import LocaleMiddleware
from django.urls import Resolver404, resolve
from django.utils.functional import cached_property


class CORSMiddleware:
    """
    Set the CORS 'Access-Control-Allow-Origin' header to allow the debug
    toolbar to work on the docs domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class ExcludeHostsLocaleMiddleware(LocaleMiddleware):
    """
    Locale middleware that lets us exclude requests to certain hosts (e.g.,
    `docs`) from being processed by LocaleMiddleware. Depends on the
    `django_hosts` middleware having processed the request.
    """

    @cached_property
    def _excluded_hosts(self):
        return frozenset(getattr(settings, "LOCALE_MIDDLEWARE_EXCLUDED_HOSTS", []))

    def _is_host_included(self, host):
        """
        Check whether the host is part of the excluded hosts list.
        """
        return host not in self._excluded_hosts

    def process_request(self, request):
        if self._is_host_included(request.host.name):
            super().process_request(request)

    def process_response(self, request, response):
        if self._is_host_included(request.host.name):
            return super().process_response(request, response)
        return response


class NormalizeSlashesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        normalized_path = re.sub(r"/{2,}", "/", path)

        if normalized_path != path:
            try:
                resolve(normalized_path)
            except Resolver404:
                pass
            else:
                return HttpResponsePermanentRedirect(normalized_path)

        return self.get_response(request)
