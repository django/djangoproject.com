"""
Register the GitHub web hook.
"""

import json
import hashlib
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
                print "Hook for %s already exists." % url
                return

        print "Creating hook for %s..." % url
        data = json.dumps({
            'name': 'web',
            'events': ['push', 'pull_request', 'issue_comment'],
            'config': {
                'url': url,
                'content_type': 'json',
                'secret': hashlib.sha1('githubwebhook' + settings.SECRET_KEY).hexdigest(),
            },
            'active': True
        })
        resp = requests.post('https://api.github.com/repos/django/django/hooks', auth=auth, data=data)
        if resp.status_code == 201:
            print "OK!"
        else:
            print "WHOOPS (%s): %s" % (resp.status_code, resp.content)
