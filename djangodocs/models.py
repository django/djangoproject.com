from django.db import models
from django.conf import settings

class DocumentReleaseManager(models.Manager):
    def default(self):
        return DocumentRelease.objects.get(is_default=True)

class DocumentRelease(models.Model):
    lang = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    version = models.CharField(max_length=20)
    scm_url = models.URLField()
    is_default = models.BooleanField()
    
    objects = DocumentReleaseManager()
    
    def __unicode__(self):
        return "%s/%s" % (self.lang, self.version)
    
    def save(self, *args, **kwargs):
        # There can be only one. Default, that is.
        if self.is_default:
            DocumentRelease.objects.update(is_default=False)
        super(DocumentRelease, self).save(*args, **kwargs)