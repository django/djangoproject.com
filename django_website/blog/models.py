import akismet
import datetime
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.comments.signals import comment_was_posted
from django.utils.encoding import smart_str
from docutils.core import publish_parts


class EntryManager(models.Manager):
    
    def active(self):
        return super(EntryManager, self).get_query_set().filter(is_active=True)

class Entry(models.Model):
    headline = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='pub_date')
    is_active = models.BooleanField(help_text="Tick to make the entry live on site (see also the publication date). Note that administrators (like yourself) are allowed to preview inactive content whereas other users and the general public aren't.", default=False)
    pub_date = models.DateTimeField(help_text='For an entry to be published, it must be active and its publication date must be in the past.')
    summary = models.TextField()
    summary_html = models.TextField(help_text="Use reStructuredText unless specified otherwise")
    body = models.TextField(help_text="Use reStructuredText unless specified otherwise")
    body_html = models.TextField()
    author = models.CharField(max_length=100)
    use_raw_html = models.BooleanField(help_text="Tick if you prefer to manually enter raw HTML instead of reStructureText formats in the summary and body. This option's main purpose is to cope with old entries that were entirely written in raw HTML.", default=False)

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
    
    @property
    def comments_enabled(self):
        delta = datetime.datetime.now() - self.pub_date
        return delta.days < 60

    def save(self, *args, **kwargs):
        if self.use_raw_html:
            self.summary_html = self.summary
            self.body_html = self.body
        else:
            settings_overrides = {
                    'doctitle_xform': False,
                    'initial_header_level': 4,
                    'id_prefix': 's-',
                }
            self.summary_html = publish_parts(source=smart_str(self.summary),
                                              writer_name="html",
                                              settings_overrides=settings_overrides)['fragment']
            self.body_html = publish_parts(source=smart_str(self.body),
                                           writer_name="html",
                                           settings_overrides=settings_overrides)['fragment']
        super(Entry, self).save(*args, **kwargs)
    
def moderate_comment(sender, comment, request, **kwargs):
    ak = akismet.Akismet(
        key = settings.AKISMET_API_KEY,
        blog_url = 'http://%s/' % Site.objects.get_current().domain
    )
    data = {
        'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERRER', ''),
        'comment_type': 'comment',
        'comment_author': smart_str(comment.user_name),
    }
    if ak.comment_check(smart_str(comment.comment), data=data, build_data=True):
        comment.is_public = False
        comment.save()
    
comment_was_posted.connect(moderate_comment)
