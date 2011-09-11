import hashlib
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from ..cla.models import find_agreements

def user_profile(request, username):
    u = get_object_or_404(User, username=username)
    ctx = {
        'user': u,
        'email_hash': hashlib.md5(u.email).hexdigest(),
        'user_can_commit': u.has_perm('auth.commit'),
        'clas': find_agreements(u),
    }
    return render(request, "accounts/user_profile.html", ctx)
