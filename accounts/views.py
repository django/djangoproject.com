import hashlib
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import caches
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from tracdb import stats as trac_stats

from .forms import ProfileForm
from .models import Profile


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "accounts/user_profile.html", {
        'user_obj': user,
        'email_hash': hashlib.md5(user.email.encode('ascii', 'ignore')).hexdigest(),
        'user_can_commit': user.has_perm('auth.commit'),
        'stats': get_user_stats(user),
    })


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('user_profile', request.user.username)
    return render(request, "accounts/edit_profile.html", {'form': form})


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
        for name in set(request.GET.getlist('user'))
    ])
    return JSONResponse(userinfo)


def get_user_info(username):
    c = caches['default']
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
            }
        c.set(key, info, 60 * 60)
    return info


def get_user_stats(user):
    c = caches['default']
    username = user.username.encode('ascii', 'ignore')
    key = 'user_vital_status:%s' % hashlib.md5(username).hexdigest()
    info = c.get(key)
    if info is None:
        info = trac_stats.get_user_stats(user.username)
        # Hide any stat with a value = 0 so that we don't accidentally insult
        # non-contributors.
        for k, v in list(info.items()):
            if v == 0:
                info.pop(k)
        c.set(key, info, 60 * 60)
    return info


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        super().__init__(
            json.dumps(obj, indent=(2 if settings.DEBUG else None)),
            content_type='application/json',
        )
