from __future__ import absolute_import

from django.http import HttpResponsePermanentRedirect, Http404
from .mapping import svn_to_git

def redirect_to_github(request, svn_revision):
    try:
        git_changeset = svn_to_git[int(svn_revision)]
    except IndexError:
        git_changeset = None
    if git_changeset is None:
        raise Http404
    github_url = 'https://github.com/django/django/commit/%s' % git_changeset
    return HttpResponsePermanentRedirect(github_url)

