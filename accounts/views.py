import hashlib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import caches
from django.shortcuts import get_object_or_404, redirect, render

from tracdb import stats as trac_stats

from .forms import ProfileForm
from .models import Profile


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(
        request,
        "accounts/user_profile.html",
        {
            "user_obj": user,
            "email_hash": hashlib.md5(user.email.encode("ascii", "ignore")).hexdigest(),
            "stats": get_user_stats(user),
        },
    )


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect("user_profile", request.user.username)
    return render(request, "accounts/edit_profile.html", {"form": form})


def get_user_stats(user):
    c = caches["default"]
    username = user.username.encode("ascii", "ignore")
    key = "user_vital_status:%s" % hashlib.md5(username).hexdigest()
    info = c.get(key)
    if info is None:
        info = trac_stats.get_user_stats(user.username)
        # Hide any stat with a value = 0 so that we don't accidentally insult
        # non-contributors.
        for k, v in list(info.items()):
            if v.count == 0:
                info.pop(k)
        c.set(key, info, 60 * 60)
    return info
