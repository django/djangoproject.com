from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomUser(AbstractBaseUser):
    new_field = models.CharField(max_length=25)
    objects = BaseUserManager()

    USERNAME_FIELD = 'new_field'
