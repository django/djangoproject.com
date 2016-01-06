from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.generic.dates import timezone_today
from sorl.thumbnail import ImageField, get_thumbnail


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


class CorporateMemberManager(models.Manager):
    def for_public_display(self):
        objs = self.get_queryset().filter(
            invoice__expiration_date__gte=timezone_today(),
        ).annotate(donated_amount=models.Sum('invoice__amount'))
        return objs.order_by('-donated_amount', 'display_name')


class CorporateMember(models.Model):
    MEMBERSHIP_LEVELS = (
        (1, 'Silver'),
        (2, 'Gold'),
        (3, 'Platinum'),
    )

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

    objects = CorporateMemberManager()

    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.display_name

    def _is_invoiced(self):
        invoices = self.invoice_set.all()
        return invoices and all(invoice.sent_date is not None for invoice in invoices)
    _is_invoiced.boolean = True
    is_invoiced = property(_is_invoiced)

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
        return get_thumbnail(self.logo, '170x170', quality=100)


@receiver(post_save, sender=CorporateMember)
def create_thumbnail_on_save(sender, **kwargs):
    return kwargs['instance'].thumbnail


class Invoice(models.Model):
    sent_date = models.DateField(blank=True, null=True)
    amount = models.IntegerField(help_text='In integer dollars')
    paid_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    member = models.ForeignKey(CorporateMember)
