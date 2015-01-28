from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils import six


@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name or six.text_type(self.user)
