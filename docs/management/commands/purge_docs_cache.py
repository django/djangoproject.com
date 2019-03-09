import sys
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.cache import caches
from django.core.management.base import BaseCommand
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--doc-versions',
            nargs='+',
            help='Limit purge to these docs versions, if possible; otherwise, purge everything '
                 '(support for selective purging is cache-dependent).',
        )

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        doc_versions = set(options['doc_versions'] or [])
        # purge Django first so Fastly doesn't immediately re-cache obsolete pages
        self.purge_django_cache()
        self.purge_fastly(doc_versions)

    def purge_django_cache(self):
        """
        If any doc versions have changed, we need to purge Django's per-site cache (in Redis) so
        any downstream caches don't immediately re-cache obsolete versions of the page.

        We have a separate 'docs-pages' cache dedicated to this purpose so other pages cached
        by the cache middleware aren't lost every time the docs get rebuilt.
        """
        caches['docs-pages'].clear()

    def purge_fastly(self, doc_versions):
        """
        Purges the Fastly surrogate key for the dev docs if that's the only version that's changed,
        or the entire cache (purge_all) if other versions have changed. Requires these settings:

        * settings.FASTLY_SERVICE_URL: the full URL to the "Django Docs" Fastly service API endpoint
          e.g., https://api.fastly.com/service/SU1Z0isxPaozGVKXdv0eY/ (a trailing slash will be
          added for you if you don't supply one)
        * settings.FASTLY_API_KEY: your Fastly API key with "purge_all" and "purge_select" scope
          for the above Django Docs service

        Any errors are echoed to self.stderr even if --verbosity=0 to make sure we get an email from
        cron about them if this task fails for any reason.
        """
        fastly_service_url = getattr(settings, 'FASTLY_SERVICE_URL', None)
        fastly_api_key = getattr(settings, 'FASTLY_API_KEY', None)
        if not (fastly_service_url and fastly_api_key):
            self.stderr.write("Fastly API key and/or service URL not found; can't purge cache")
            # make sure Ansible sees this as a failure
            sys.exit(1)
        # Make sure fastly_service_url ends with a trailing slash; otherwise, urljoin() will lop off
        # the last part of the path. If needed, urljoin() will remove any duplicate slashes for us.
        fastly_service_url += '/'
        s = requests.Session()
        # make some allowance for temporary network failures for our .post() request below
        retry = Retry(total=5, method_whitelist={'POST'}, backoff_factor=0.1)
        s.mount(fastly_service_url, HTTPAdapter(max_retries=retry))
        s.headers.update({
            'Fastly-Key': fastly_api_key,
            'Accept': 'application/json',
        })
        if doc_versions == {'dev'}:
            # If only the dev docs have changed, we can purge only the surrogate key we've set
            # up for the dev docs release in Fastly. This will usually happen with every new commit
            # to django master (on the next hour, when the cron job runs).
            url = urljoin(fastly_service_url, 'purge/dev-docs-key')
        else:
            # Otherwise, just purge everything, to keep things simple. This will usually only happen
            # around a release when we want these pages to update as soon as possible anyways.
            url = urljoin(fastly_service_url, 'purge_all')
        if self.verbosity >= 1:
            self.stdout.write("Purging Fastly cache: %s" % url)
        result = s.post(url).json()
        if result.get('status') != 'ok':
            self.stderr.write("WARNING: Fastly purge failed for URL: %s; result=%s" % (url, result))
            sys.exit(1)
