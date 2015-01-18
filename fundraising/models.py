from datetime import date
from decimal import Decimal

from django.db import models

WEEKLY_GOAL = Decimal("2800.00")
DISPLAY_LOGO_AMOUNT = Decimal("350.0")
START_DATE = date(2014, 11, 1)


class DjangoHeroManager(models.Manager):
    def in_period(self, begin, end, with_logo=False):
        donors = self.get_queryset().filter(
            donation__date__gte=begin,
            donation__date__lt=end,
            is_visible=True,
        ).annotate(donated_amount=models.Sum('donation__amount'))

        if with_logo:
            donors = donors.filter(donated_amount__gte=DISPLAY_LOGO_AMOUNT)
        else:
            donors = donors.filter(donated_amount__lt=DISPLAY_LOGO_AMOUNT)

        return donors.order_by('-donated_amount', 'name')


class DjangoHero(models.Model):
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to="fundraising/logos/", blank=True)
    url = models.URLField(blank=True)
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
    created = models.DateTimeField(auto_now_add=True)

    objects = DjangoHeroManager()

    def __unicode__(self):
        return self.name if self.name else 'Anonymous #{}'.format(self.pk)


class Donation(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    date = models.DateTimeField()
    donor = models.ForeignKey(DjangoHero, null=True)

    def __unicode__(self):
        return '${}'.format(self.amount)
