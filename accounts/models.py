from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name or str(self.user)


class TracAccountQuerySet(models.QuerySet):
    def is_username_verified_for_another_user(self, user, username=None):
        return self.exclude(user=user).filter(username=username or user.username).exists()

class TracAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(
        max_length=150,
        db_index=True,
        help_text=mark_safe(
            _(
                "<p>⚠️ The username on Trac. <b>Setting this verifies ownership.</b></p>"
                "<p>"
                "While a Trac account can be linked to multiple users, once claimed, any user "
                "with a matching <code>djangoproject.com</code> username who lacks their own "
                "verified Trac account will no longer be able to display Trac stats on their profile."
                "</p>",
            ),
        ),
    )
    objects = TracAccountQuerySet.as_manager()

    class Meta:
        unique_together = [
            ("user", "username"),
        ]

    def __str__(self):
        return f"Trac account for {self.user}: {self.username}"
