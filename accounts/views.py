import hashlib
from urllib.parse import urlencode

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render

from tracdb import stats as trac_stats

from .forms import DeleteProfileForm, ProfileForm
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


@login_required
def delete_profile(request):
    if request.method == "POST":
        form = DeleteProfileForm(data=request.POST, user=request.user)
        if form.is_valid() and form.delete():
            logout(request)
            return redirect("delete_profile_success")
    else:
        form = DeleteProfileForm(user=request.user)

    context = {
        "form": form,
        # Strings are left untranslated on purpose (ops prefer english :D)
        "OPS_EMAIL_PRESETS": urlencode(
            {
                "subject": "[djangoproject.com] Manual account deletion",
                "body": (
                    "Hello lovely Django Ops,\n\n"
                    "I would like to delete my djangoproject.com user account ("
                    f"username {request.user.username}) but the system is not letting "
                    "me do it myself. Could you help me out please?\n\n"
                    "Thanks in advance,\n"
                    "You're amazing\n"
                    f"{request.user.get_full_name() or request.user.username}"
                ),
            }
        ),
    }
    return render(request, "accounts/delete_profile.html", context)


def delete_profile_success(request):
    return render(request, "accounts/delete_profile_success.html")


def get_user_stats(user):
    username = user.username.encode("ascii", "ignore")
    key = "user_vital_status:%s" % hashlib.md5(username).hexdigest()
    info = cache.get(key)
    if info is None:
        info = trac_stats.get_user_stats(user.username)
        # Hide any stat with a value = 0 so that we don't accidentally insult
        # non-contributors.
        for k, v in list(info.items()):
            if v.count == 0:
                info.pop(k)
        cache.set(key, info, 60 * 60)
    return info
