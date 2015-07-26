from django.db import models
from django.views.generic.dates import timezone_today


class DeveloperMember(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField()
    member_since = models.DateField(default=timezone_today)
    member_until = models.DateField(null=True, blank=True)
    reason_for_leaving = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.member_until is None


class CorporateMember(models.Model):
    MEMBERSHIP_LEVELS = (
        (1, 'Independent consultancy'),
        (2, 'Small-to-medium business'),
        (3, 'Large corporation'),
    )

    display_name = models.CharField(max_length=250)
    formal_name = models.CharField(max_length=250)
    logo = models.ImageField(upload_to='corporate-members', null=True, blank=True)
    description = models.TextField()
    url = models.URLField()
    contact_email = models.EmailField()
    billing_email = models.EmailField()
    initial_contact_date = models.DateField(default=timezone_today)
    membership_level = models.IntegerField(choices=MEMBERSHIP_LEVELS)
    membership_start = models.DateField()
    membership_expires = models.DateField()
    address = models.TextField()

    def __str__(self):
        return self.display_name
