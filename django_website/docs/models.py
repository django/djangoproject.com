from django.db import models
from django.conf import settings
from django.core.cache import cache

class DocumentReleaseManager(models.Manager):
    def default(self):
        return DocumentRelease.objects.get(is_default=True)

class DocumentRelease(models.Model):
    """
    A "release" of documentation -- i.e. English for v1.2.
    """
    DEFAULT_CACHE_KEY = "%s_recent_release" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
    SVN = 'svn'
    SCM_CHOICES = (
        (SVN, 'SVN'),
    )
    
    lang = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    version = models.CharField(max_length=20)
    scm = models.CharField(max_length=10, choices=SCM_CHOICES)
    scm_url = models.URLField()
    is_default = models.BooleanField()
    
    objects = DocumentReleaseManager()
    
    def __unicode__(self):
        return "%s/%s" % (self.lang, self.version)
    
    @models.permalink
    def get_absolute_url(self):
        return ('document-index', [], {'lang': self.lang, 'version': self.version})
            
    def save(self, *args, **kwargs):
        # There can be only one. Default, that is.
        if self.is_default:
            DocumentRelease.objects.update(is_default=False)
            cache.set(
                self.DEFAULT_CACHE_KEY,
                self.version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        super(DocumentRelease, self).save(*args, **kwargs)
    
