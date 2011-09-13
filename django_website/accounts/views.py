from __future__ import absolute_import

import hashlib
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
from django.core import cache
from django.http import HttpResponse
from ..trac import stats as trac_stats
from ..cla.models import find_agreements

def user_profile(request, username):
    u = get_object_or_404(User, username=username)
    ctx = {
        'profile': u,
        'email_hash': hashlib.md5(u.email).hexdigest(),
        'user_can_commit': u.has_perm('auth.commit'),
        'clas': find_agreements(u),
        'stats': get_user_stats(u),
    }
    return render(request, "accounts/user_profile.html", ctx)

def json_user_info(request):
    """
    Return info about some users as a JSON object.

    Part of a set of hacks that feed more info into Trac. This takes
    a list of users as GET['user'] and returns a JSON object::

        {
            {USERNAME: {"core": false, "cla": true}},
            {USERNAME: {"core": false, "cla": true}},
            ...
        }

    De-duplication on GET['user'] is performed since I don't want to have to
    think about how best to do it in JavaScript :)
    """

    userinfo = dict([
                (name, get_user_info(name))
                for name in set(request.GET.getlist('user'))])
    return JSONResponse(userinfo)

def get_user_info(username):
    c = cache.get_cache('default')
    username = username.encode('ascii', 'ignore')
    key = 'trac_user_info:%s' % hashlib.md5(username).hexdigest()
    info = c.get(key)
    if info is None:
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            info = {"core": False, "cla": False}
        else:
            info = {
                "core": u.has_perm('auth.commit'),
                "cla": bool(find_agreements(u))
            }
        c.set(key, info, 60*60)
    return info

def get_user_stats(user):
    c = cache.get_cache('default')
    key = 'user_vital_status:%s' % hashlib.md5(user.username).hexdigest()
    info = c.get(key)
    if info is None:
        info = trac_stats.get_user_stats(user.username)
        # Hide any stat with a value = 0 so that we don't accidentally insult
        # non-contributors.
        for k, v in info.items():
            if v == 0:
                info.pop(k)
        c.set(key, info, 60*60)
    return info

class JSONResponse(HttpResponse):
    def __init__(self, obj):
        super(JSONResponse, self).__init__(
            json.dumps(obj, indent=(2 if settings.DEBUG else None)),
            content_type='application/json',
        )
