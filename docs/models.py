from django.conf import settings
from django.core.cache import cache
from django.db import models

class DocumentReleaseManager(models.Manager):
    def default(self):
        return DocumentRelease.objects.get(is_default=True)

    def default_version(self):
        default_version = cache.get(DocumentRelease.DEFAULT_CACHE_KEY)
        if not default_version:
            try:
                default_version = DocumentRelease.objects.default().version
            except DocumentRelease.DoesNotExist:
                default_version = 'dev'
            cache.set(
                DocumentRelease.DEFAULT_CACHE_KEY,
                default_version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        return default_version

class DocumentRelease(models.Model):
    """
    A "release" of documentation -- i.e. English for v1.2.
    """
    DEFAULT_CACHE_KEY = "%s_recent_release" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
    SVN = 'svn'
    GIT = 'git'
    SCM_CHOICES = (
        (SVN, 'SVN'),
        (GIT, 'git'),
    )

    lang = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    version = models.CharField(max_length=20)
    scm = models.CharField(max_length=10, choices=SCM_CHOICES)
    scm_url = models.CharField(max_length=200)
    docs_subdir = models.CharField(max_length=200, blank=True)
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

    @property
    def human_version(self):
        """
        Return a "human readable" version of the version.
        """
        return "Development trunk" if self.is_dev else "Django %s" % self.version

    @property
    def is_dev(self):
        return self.version == 'dev'

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
        if self.path:
            kwargs = {
                'lang': self.release.lang,
                'version': self.release.version,
                'url': self.path,
            }
            return ('document-detail', [], kwargs)
        else:
            kwargs = {
                'lang': self.release.lang,
                'version': self.release.version,
            }
            return ('document-index', [], kwargs)
