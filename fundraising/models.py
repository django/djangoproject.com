from django.db import models

class DjangoHero(models.Model):
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to="fundraising/logos/", blank=True)
    url = models.URLField(blank=True)
    name = models.CharField(max_length=100, blank=True)
    is_visible = models.BooleanField(default=False, verbose_name="Agreed to displaying on the fundraising page?")
    is_subscribed = models.BooleanField(default=False, verbose_name="Agreed to being contacted by DSF?")
    is_amount_displayed = models.BooleanField(default=False, verbose_name="Agreed to disclose amount of donation?")
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name if self.name else 'Anonymous #{}'.format(self.pk)
