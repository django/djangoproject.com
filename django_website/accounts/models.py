from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name or unicode(self.user)
