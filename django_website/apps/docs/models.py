from django.db import models

class DocumentRelease(models.Model):
    version = models.CharField(max_length=20, unique=True)
    repository_path = models.CharField(max_length=50, help_text="(i.e. 'tags/releases/0.95' or 'branches/0.95-bugfixes')")
    release_date = models.DateField()
    
    class Meta:
        ordering = ('-release_date',)
        
    class Admin:
        list_display = ("version", "repository_path", "release_date")
        
    def __unicode__(self):
        return self.version
    
    def get_absolute_url(self):
        return "/documentation/%s/" % (self.version)
    
