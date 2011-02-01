from django.db import models
from django.conf import settings

class DocumentReleaseManager(models.Manager):
    def default(self):
        return DocumentRelease.objects.get(is_default=True)

class DocumentRelease(models.Model):
    """
    A "release" of documentation -- i.e. English for v1.2.
    """
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
        super(DocumentRelease, self).save(*args, **kwargs)
    
    @property
    def human_version(self):
        """
        Return a "human readable" version of the version.
        """
        return "Development trunk" if self.version == 'dev' \
                                   else "Django %s" % self.version

class Document(models.Model):
    """
    An individual document. Used mainly as a hook point for Haystack.
    """
    release = models.ForeignKey(DocumentRelease, related_name='documents')
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=500)

    def __unicode__(self):
        return "/".join([self.release.lang, self.release.version, self.path])

    @models.permalink
    def get_absolute_url(self):
        kwargs = {
            'lang': self.release.lang,
            'version': self.release.version,
            'url': self.path
        }
        return ('document-detail', [], kwargs)
