"""
Remove a previously-installed GitHub web hook.
"""

import json
import optparse
import requests
from django.conf import settings
from django.core import urlresolvers
from django.core.management.base import NoArgsCommand
from ... import github

class Command(NoArgsCommand):
    help = __doc__.strip()
    option_list = NoArgsCommand.option_list + (
        optparse.make_option('--base-url',
            default = "https://www.djangoproject.com/",
            help = ("Base URL for the web hook; useful for local testing. "
                    "Defaults to https://www.djangoproject.com/")
        ),
    )

    def handle_noargs(self, **options):
        url = "%s/%s" % (options['base_url'].rstrip('/'), urlresolvers.reverse('github_webhook').lstrip('/'))
        with github.session() as gh:
            for hook in gh.get('repos/django/django/hooks').json:
                if hook['name'] == 'web' and hook['config']['url'] == url:
                    print "Deleting hook for %s..." % url
                    resp = gh.delete(hook['url'])
                    if resp.status_code == 204:
                        print "OK!"
                    else:
                        print "WHOOPS (%s): %s", (resp.status_code, resp.content)
                    break
            else:
                print "No hook for %s found." % url
