from collections import defaultdict

from django.core import signing
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.generic.dates import timezone_today
from django_hosts import reverse
from sorl.thumbnail import ImageField, get_thumbnail

BRONZE_MEMBERSHIP = 1
SILVER_MEMBERSHIP = 2
GOLD_MEMBERSHIP = 3
PLATINUM_MEMBERSHIP = 4
DIAMOND_MEMBERSHIP = 5

CORPORATE_MEMBERSHIP_AMOUNTS = {
    'diamond': 100000,
    'platinum': 30000,
    'gold': 12500,
    'silver': 5000,
    'bronze': 2000,
}

MEMBERSHIP_LEVELS = (
    (BRONZE_MEMBERSHIP, 'Bronze'),
    (SILVER_MEMBERSHIP, 'Silver'),
    (GOLD_MEMBERSHIP, 'Gold'),
    (PLATINUM_MEMBERSHIP, 'Platinum'),
    (DIAMOND_MEMBERSHIP, 'Diamond'),
)

MEMBERSHIP_TO_KEY = dict((k, v.lower()) for k, v in MEMBERSHIP_LEVELS)


class IndividualMember(models.Model):
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


class Team(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField()
    description = models.TextField(help_text='HTML, without surrounding <p> tags.')
    members = models.ManyToManyField(IndividualMember)

    def __str__(self):
        return self.name


class CorporateMemberManager(models.Manager):
    def for_public_display(self):
        objs = self.get_queryset().filter(
            invoice__expiration_date__gte=timezone_today(),
        ).annotate(donated_amount=models.Sum('invoice__amount'))
        return objs.order_by('-donated_amount', 'display_name')

    def by_membership_level(self):
        members_by_type = defaultdict(list)
        members = self.for_public_display()
        for member in members:
            key = MEMBERSHIP_TO_KEY[member.membership_level]
            members_by_type[key].append(member)
        return members_by_type


class CorporateMember(models.Model):
    display_name = models.CharField(max_length=250)
    billing_name = models.CharField(
        max_length=250,
        blank=True,
        help_text='If different from display name.',
    )
    logo = ImageField(upload_to='corporate-members', null=True, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(verbose_name='URL')
    contact_name = models.CharField(max_length=250)
    contact_email = models.EmailField()
    billing_email = models.EmailField(blank=True, help_text='If different from contact email.',)
    membership_level = models.IntegerField(choices=MEMBERSHIP_LEVELS)
    address = models.TextField(blank=True)
    django_usage = models.TextField(blank=True, help_text='Not displayed publicly.')
    notes = models.TextField(blank=True, help_text='Not displayed publicly.')
    inactive = models.BooleanField(default=False, help_text='No longer renewing.')

    objects = CorporateMemberManager()

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name

    def _is_invoiced(self):
        invoices = self.invoice_set.all()
        return bool(invoices) and all(invoice.sent_date is not None for invoice in invoices)
    _is_invoiced.boolean = True
    is_invoiced = property(_is_invoiced)

    def _is_paid(self):
        invoices = self.invoice_set.all()
        return bool(invoices) and all(invoice.paid_date is not None for invoice in invoices)
    _is_paid.boolean = True
    is_paid = property(_is_paid)

    def get_expiry_date(self):
        expiry_date = None
        for invoice in self.invoice_set.all():
            if expiry_date is None:
                expiry_date = invoice.expiration_date
            elif invoice.expiration_date and invoice.expiration_date > expiry_date:
                expiry_date = invoice.expiration_date
        return expiry_date

    @property
    def thumbnail(self):
        return get_thumbnail(self.logo, '170x170', quality=100) if self.logo else None

    def get_renewal_link(self):
        return reverse('members:corporate-members-renew', kwargs={'token': signing.dumps(self.pk)})


@receiver(post_save, sender=CorporateMember)
def create_thumbnail_on_save(sender, **kwargs):
    return kwargs['instance'].thumbnail


class Invoice(models.Model):
    sent_date = models.DateField(blank=True, null=True)
    amount = models.IntegerField(help_text='In integer dollars')
    paid_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    member = models.ForeignKey(CorporateMember, on_delete=models.CASCADE)
