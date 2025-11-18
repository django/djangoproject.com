from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    trac_username = models.CharField(
        max_length=150,
        blank=True,
        null=False,
        default="",
        db_index=True,
    )

    def __str__(self):
        return self.name or str(self.user)
