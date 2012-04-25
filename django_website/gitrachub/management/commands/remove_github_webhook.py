"""
Remove a previously-installed GitHub web hook.
"""

import json
import optparse
import requests
from django.conf import settings
from django.core import urlresolvers
from django.core.management.base import NoArgsCommand

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
        auth = tuple(settings.GITHUB_CREDS)
        url = "%s/%s" % (options['base_url'].rstrip('/'), urlresolvers.reverse('github_webhook').lstrip('/'))
        hooks = json.loads(requests.get('https://api.github.com/repos/django/django/hooks', auth=auth).content)
        for hook in hooks:
            if hook['name'] == 'web' and hook['config']['url'] == url:
                print "Deleting hook for %s..." % url
                resp = requests.delete(hook['url'], auth=auth)
                if resp.status_code == 204:
                    print "OK!"
                else:
                    print "WHOOPS (%s): %s", (resp.status_code, resp.content)
                break
        else:
            print "No hook for %s found." % url
