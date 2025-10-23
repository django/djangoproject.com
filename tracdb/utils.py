from contextlib import suppress

from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_trac_username(user):
    with suppress(User.profile.RelatedObjectDoesNotExist):
        if user.profile.trac_username:
            return user.profile.trac_username
    return user.username
