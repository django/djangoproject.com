from django.db import models
from django.views.generic.dates import timezone_today


class DeveloperMember(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    member_since = models.DateField(default=timezone_today)
    member_until = models.DateField(null=True, blank=True)
    reason_for_leaving = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

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
    billing_name = models.CharField(
        max_length=250,
        blank=True,
        help_text='If different from display name.',
    )
    logo = models.ImageField(upload_to='corporate-members', null=True, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(verbose_name='URL')
    contact_name = models.CharField(max_length=250)
    contact_email = models.EmailField()
    billing_email = models.EmailField(blank=True, help_text='If different from contact email.',)
    membership_level = models.IntegerField(choices=MEMBERSHIP_LEVELS)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name


class Invoice(models.Model):
    sent_date = models.DateField()
    amount = models.IntegerField(help_text='In integer dollars')
    paid_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    member = models.ForeignKey(CorporateMember)
