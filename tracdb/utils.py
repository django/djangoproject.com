from contextlib import suppress

from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


def get_user_trac_username(user):
    with suppress(User.profile.RelatedObjectDoesNotExist):
        if user.profile.trac_username:
            return user.profile.trac_username
    return user.username


def check_if_trac_username_is_overridden_for_user(user):
    with suppress(User.profile.RelatedObjectDoesNotExist):
        if user.profile.trac_username:
            return True
    return False


def check_if_trac_username_is_overridden_for_another_user(user):
    return (
        Profile.objects.exclude(user_id=user.pk)
        .filter(trac_username=user.username)
        .exists()
    )


def check_if_public_trac_stats_are_renderable_for_user(user):
    # When `Profile.trac_username` is set for a user, this means that it's
    # verified that they own that Trac username. But this also means that
    # no more djangoproject.com user should use that username to retrieve the
    # public stats, unless the accounts belong to the same user (if this is the
    # case, please set the same `trac_username` for both users).
    return check_if_trac_username_is_overridden_for_user(
        user
    ) or not check_if_trac_username_is_overridden_for_another_user(user)
