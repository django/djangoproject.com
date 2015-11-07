from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import crypto, timezone
from django_hosts.resolvers import reverse
from sorl.thumbnail import ImageField, get_thumbnail

DISPLAY_LOGO_AMOUNT = Decimal("200.00")
DEFAULT_DONATION_AMOUNT = 50
INTERVAL_CHOICES = (
    ('monthly', 'Monthly donation'),
    ('quarterly', 'Quarterly donation'),
    ('yearly', 'Yearly donation'),
    ('onetime', 'One-time donation'),
)


class DjangoHeroManager(models.Manager):
    def for_campaign(self, campaign, hero_type=None):
        donors = self.get_queryset().filter(
            donation__campaign=campaign,
            is_visible=True,
            approved=True,
        ).annotate(donated_amount=models.Sum('donation__payment__amount'))

        if hero_type:
            donors = donors.filter(hero_type=hero_type)

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
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    logo = ImageField(upload_to="fundraising/logos/", blank=True)
    url = models.URLField(blank=True, verbose_name='URL')
    name = models.CharField(max_length=100, blank=True)
    HERO_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('organization', 'Organization'),
    )
    hero_type = models.CharField(max_length=30, choices=HERO_TYPE_CHOICES, blank=True)
    is_visible = models.BooleanField(
        default=False,
        verbose_name="Agreed to displaying on the fundraising page?",
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name="Agreed to being contacted by DSF?",
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


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    goal = models.DecimalField(max_digits=9, decimal_places=2)
    template = models.CharField(max_length=50, default="fundraising/campaign_default.html")
    stretch_goal = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    stretch_goal_url = models.URLField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False, help_text="Should donation form be enabled or not?")
    is_public = models.BooleanField(default=False, help_text="Should campaign be visible at all?")

    def __str__(self):
        return self.name

    @classmethod
    def get_active_campaign(cls):
        return cls.objects.filter(
            is_public=True, is_active=True
        ).order_by("-start_date").first()


class Donation(FundraisingModel):
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, blank=True)
    subscription_amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    donor = models.ForeignKey(DjangoHero, null=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    receipt_email = models.EmailField(blank=True)

    def __str__(self):
        return '{} from {}'.format(self.get_interval_display(), self.donor)

    def get_absolute_url(self):
        return reverse('fundraising:thank-you', kwargs={'donation': self.id})

    def total_payments(self):
        return self.payment_set.aggregate(models.Sum('amount'))['amount__sum']


class Payment(models.Model):
    donation = models.ForeignKey(Donation)
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '${}'.format(self.amount)


class Testimonial(models.Model):
    campaign = models.ForeignKey(Campaign, null=True)
    author = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.author
