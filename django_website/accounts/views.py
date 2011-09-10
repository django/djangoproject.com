from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def user_profile(request, username):
    u = get_object_or_404(User, username=username)
    ctx = {'user': u, 'user_can_commit': u.has_perm('auth.commit')}
    return render(request, "accounts/user_profile.html", ctx)
