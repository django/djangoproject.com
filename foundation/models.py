from django.conf import settings
from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from docutils.core import publish_parts

CONTENT_FORMAT_CHOICES = (
    ('reST', 'reStructuredText'),
    ('html', 'Raw HTML'),
)

BLOG_DOCUTILS_SETTINGS = {
    'doctitle_xform': False,
    'initial_header_level': 3,
    'id_prefix': 's-',
    'raw_enabled': False,
    'file_insertion_enabled': False,
}
BLOG_DOCUTILS_SETTINGS.update(getattr(settings, 'BLOG_DOCUTILS_SETTINGS', {}))


class BoardMinutes(models.Model):
    """Board Minutes Model"""

    content_format = models.CharField(choices=CONTENT_FORMAT_CHOICES, max_length=50)
    body = models.TextField()
    slug = models.SlugField(unique_for_date='date')
    date = models.DateField()

    class Meta:
        verbose_name_plural = 'Board Minutes'
        ordering = ['-date']
        get_latest_by = 'id'

    @staticmethod
    def get_absolute_url():
        return reverse('board-minutes-list')

    def __str__(self):
        return "{}".format(self.date)

    def save(self, *args, **kwargs):
        if self.content_format == 'html':
            self.body = self.body
        elif self.content_format == 'reST':
            self.body = publish_parts(source=self.body,
                                      writer_name='html',
                                      settings_overrides=BLOG_DOCUTILS_SETTINGS)['fragment']
        super().save(*args, **kwargs)


def pre_save_board_minutes_receiver(sender, instance, *args, **kwargs):
    """ A signal for unique slug generator.
    If a slug already exists the latest id is appended to the new slug.
    """
    slug = slugify(instance.date)
    if BoardMinutes.objects.filter(slug=slug).exists():
        latest = BoardMinutes.objects.latest()
        slug = "{}-{}".format(slug, latest.id)
    instance.slug = slug


pre_save.connect(pre_save_board_minutes_receiver, sender=BoardMinutes)
