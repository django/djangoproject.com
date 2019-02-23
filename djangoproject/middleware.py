from django.conf import settings
from django.http.request import split_domain_port
from django.middleware.locale import LocaleMiddleware
from django.utils.functional import cached_property
from django.utils.http import is_same_domain


class CORSMiddleware(object):
    """
    Set the CORS 'Access-Control-Allow-Origin' header to allow the debug
    toolbar to work on the docs domain.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        return response


class ExcludeHostsLocaleMiddleware(LocaleMiddleware):
    """
    Locale middleware that lets us exclude requests to certain hosts (e.g.,
    docs.djangoproject.com) from being processed by LocaleMiddleware.
    """

    @cached_property
    def _excluded_hosts(self):
        return frozenset(getattr(settings, 'LOCALE_MIDDLEWARE_EXCLUDED_HOSTS', []))

    def _is_host_included(self, host):
        """
        Mirrors the behavior of django.http.request.validate_host(), but does
        not match '*' (which would exclude all hosts). To exclude all requests
        from being processed by LocaleMiddleware one should simply remove this
        class from settings.MIDDLEWARE.
        """
        domain, _ = split_domain_port(host)
        return not any(is_same_domain(domain, pattern) for pattern in self._excluded_hosts)

    def process_request(self, request):
        if self._is_host_included(request.get_host()):
            super().process_request(request)

    def process_response(self, request, response):
        if self._is_host_included(request.get_host()):
            return super().process_response(request, response)
        return response
