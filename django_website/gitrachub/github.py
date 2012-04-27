"""
Teeny-tiny GitHub API wrapper (just for the bits this app needs).

All that this does is expose a `requests.session` that makes it easy to
access GitHub, like so::

    >>> with github.session() as gh:
    ...     resp = gh.get('repos/django/django')
    ...     print resp.keys()

What this does:

    * Pulls auth from settings.GITHUB_AUTH if not otherwise provided.
    * Prefixes URLs with "https://api.github.com/".
    * Automatically encode JSON in the request `data` arguments.
    * Automatically decode JSON into `request.json` (because `request.content`
      isn't writeable).
"""

import re
import json
import requests
from django.conf import settings

def session(auth=None):
    return requests.session(
        auth = auth or tuple(settings.GITHUB_CREDS),
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        },
        hooks = {
            'args': _mangle_args,
            'response': _mangle_response
        }
    )

def _mangle_args(args):
    """
    Prefix URLs with the GitHub API prefix, and encode data into JSON if given.
    """
    # Prefix URLs
    if not args['url'].startswith('https://'):
        args['url'] = 'https://api.github.com/' + args['url'].lstrip('/')

    # Encode JSON
    if args['data'] and not isinstance(args['data'], basestring):
        args['data'] = json.dumps(args['data'])

    return args

def _mangle_response(response):
    """
    Decode JSON from response.content into response.json and parse the link header.
    """
    # Decode JSON
    if 'json' in response.headers.get('Content-Type', ''):
        response.json = json.loads(response.content)

    # Parse the Link header
    if 'link' in response.headers:
        link_re = re.compile(r'<([^>]+)>; rel="([^"]+)"')
        response.links = {}
        for link in response.headers['link'].split(','):
            m = link_re.search(link)
            response.links[m.group(2)] = m.group(1)

    return response
