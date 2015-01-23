from decimal import Decimal

from django.db import models
from django.dispatch import receiver
from django.utils import crypto, timezone
from django.db.models.signals import post_save
from django_hosts.resolvers import reverse

from sorl.thumbnail import get_thumbnail, ImageField

RESTART_GOAL = Decimal("30000.00")
STRETCH_GOAL = Decimal("50000.00")
WEEKLY_GOAL = Decimal("2800.00")
DISPLAY_LOGO_AMOUNT = Decimal("200.00")
DEFAULT_DONATION_AMOUNT = Decimal("50.00")


class DjangoHeroManager(models.Manager):
    def in_period(self, begin, end, with_logo=False):
        donors = self.get_queryset().filter(
            donation__created__gte=begin,
            donation__created__lt=end,
            is_visible=True,
            approved=True,
        ).annotate(donated_amount=models.Sum('donation__amount'))

        if with_logo:
            donors = donors.filter(donated_amount__gte=DISPLAY_LOGO_AMOUNT)
        else:
            donors = donors.filter(donated_amount__lt=DISPLAY_LOGO_AMOUNT)

        return donors.order_by('-donated_amount', 'name')


class FundraisingModel(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        if not self.id:
            self.id = crypto.get_random_string(length=12)
        return super(FundraisingModel, self).save(*args, **kwargs)


class DjangoHero(FundraisingModel):
    email = models.EmailField(blank=True)
    logo = ImageField(upload_to="fundraising/logos/", blank=True)
    url = models.URLField(blank=True, verbose_name='URL')
    name = models.CharField(max_length=100, blank=True)
    is_visible = models.BooleanField(
        default=False,
        verbose_name="Agreed to displaying on the fundraising page?",
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Agreed to being contacted by DSF?",
    )
    is_amount_displayed = models.BooleanField(
        default=False,
        verbose_name="Agreed to disclose amount of donation?",
    )
    approved = models.NullBooleanField(
        verbose_name="Name, URL, and Logo approved?",
    )

    objects = DjangoHeroManager()

    def __str__(self):
        return self.name if self.name else 'Anonymous #{}'.format(self.pk)

    class Meta:
        verbose_name = "Django hero"
        verbose_name_plural = "Django heroes"

    @property
    def thumbnail(self):
        return get_thumbnail(self.logo, '170x170', quality=100)

    @property
    def name_with_fallback(self):
        return self.name if self.name else 'Anonymous Hero'


@receiver(post_save, sender=DjangoHero)
def create_thumbnail_on_save(sender, **kwargs):
    return kwargs['instance'].thumbnail


class Donation(FundraisingModel):
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    donor = models.ForeignKey(DjangoHero, null=True)
    stripe_charge_id = models.CharField(max_length=100, null=True)
    stripe_customer_id = models.CharField(max_length=100, null=True)
    campaign_name = models.CharField(max_length=100, blank=True)
    receipt_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return '${}'.format(self.amount)

    def get_absolute_url(self):
        return reverse('fundraising:thank-you', kwargs={'donation': self.id})


class Testimonial(models.Model):
    author = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.author
