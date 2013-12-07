import datetime
from docutils.core import publish_parts

from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _


BLOG_DOCUTILS_SETTINGS = getattr(settings, 'BLOG_DOCUTILS_SETTINGS', {
    'doctitle_xform': False,
    'initial_header_level': 4,
    'id_prefix': 's-',
})


class EntryManager(models.Manager):

    def published(self):
        return self.active().filter(pub_date__lte=datetime.datetime.now())

    def active(self):
        return super(EntryManager, self).get_queryset().filter(is_active=True)

CONTENT_FORMAT_CHOICES = (
    (u'reST', u'reStructuredText'),
    (u'html', u'Raw HTML'),
)

class Entry(models.Model):
    headline = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='pub_date')
    is_active = models.BooleanField(help_text=_("Tick to make this entry live (see also the publication date). Note that administrators (like yourself) are allowed to preview inactive entries whereas the general public aren't."), default=False)
    pub_date = models.DateTimeField(verbose_name=_("Publication date"), help_text=_("For an entry to be published, it must be active and its publication date must be in the past."))
    content_format = models.CharField(choices=CONTENT_FORMAT_CHOICES, max_length=50)
    summary = models.TextField()
    summary_html = models.TextField()
    body = models.TextField()
    body_html = models.TextField()
    author = models.CharField(max_length=100)

    objects = EntryManager()

    class Meta:
        db_table = 'blog_entries'
        verbose_name_plural = 'entries'
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __unicode__(self):
        return self.headline

    def get_absolute_url(self):
        return "/weblog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)

    def is_published(self):
        """
        Return True if the entry is publicly accessible.
        """
        return self.is_active and self.pub_date <= datetime.datetime.now()
    is_published.boolean = True

    def save(self, *args, **kwargs):
        if self.content_format == u'html':
            self.summary_html = self.summary
            self.body_html = self.body
        elif self.content_format == u'reST':
            self.summary_html = publish_parts(source=smart_str(self.summary),
                                              writer_name="html",
                                              settings_overrides=BLOG_DOCUTILS_SETTINGS)['fragment']
            self.body_html = publish_parts(source=smart_str(self.body),
                                           writer_name="html",
                                           settings_overrides=BLOG_DOCUTILS_SETTINGS)['fragment']
        super(Entry, self).save(*args, **kwargs)
