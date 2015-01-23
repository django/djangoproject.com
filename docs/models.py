import json
import operator
import os
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.functional import cached_property

from django_hosts.resolvers import reverse

from . import utils
from functools import reduce


class DocumentReleaseManager(models.Manager):

    def current(self, lang='en'):
        current = self.get(is_default=True)
        if lang != 'en':
            try:
                return self.get(lang=lang, version=current.version)
            except DocumentRelease.DoesNotExist:
                pass
        return current

    def current_version(self):
        current_version = cache.get(DocumentRelease.DEFAULT_CACHE_KEY)
        if not current_version:
            try:
                current_version = self.current().version
            except DocumentRelease.DoesNotExist:
                current_version = 'dev'
            cache.set(
                DocumentRelease.DEFAULT_CACHE_KEY,
                current_version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        return current_version


class DocumentRelease(models.Model):
    """
    A "release" of documentation -- i.e. English for v1.2.
    """
    DEFAULT_CACHE_KEY = "%s_docs_version" % settings.CACHE_MIDDLEWARE_KEY_PREFIX
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
    is_default = models.BooleanField(default=False)

    objects = DocumentReleaseManager()

    class Meta:
        unique_together = ('lang', 'version')

    def __str__(self):
        return "%s/%s" % (self.lang, self.version)

    def get_absolute_url(self):
        kwargs = {
            'lang': self.lang,
            'version': self.version,
        }
        return reverse('document-index', host='docs', kwargs=kwargs)

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
        return "development" if self.is_dev else self.version

    @property
    def is_dev(self):
        return self.version == 'dev'


def document_url(doc):
    if doc.path:
        kwargs = {
            'lang': doc.release.lang,
            'version': doc.release.version,
            'url': doc.path,
        }
        return reverse('document-detail', host='docs', kwargs=kwargs)
    else:
        kwargs = {
            'lang': doc.release.lang,
            'version': doc.release.version,
        }
        return reverse('document-index', host='docs', kwargs=kwargs)


class DocumentManager(models.Manager):

    def parents(self, path):
        """Iterate over this path's parents, in ascending order."""
        for segment in os.path.split(str(path))[1:]:  # ignores the root element
            yield Path(segment)

    def breadcrumbs(self, document):
        or_queries = [models.Q(path=path)
                      for path in self.parents(Path(document.path))]
        if or_queries:
            return (self.filter(reduce(operator.or_, or_queries))
                        .filter(release=document.release)
                        .exclude(pk=document.pk)
                        .order_by('path'))
        return self.none()


class Document(models.Model):
    """
    An individual document. Used mainly as a hook point for the search.
    """
    release = models.ForeignKey(DocumentRelease, related_name='documents')
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=500)

    objects = DocumentManager()

    class Meta:
        unique_together = ('release', 'path')

    def __str__(self):
        return "/".join([self.release.lang, self.release.version, self.path])

    def get_absolute_url(self):
        return document_url(self)

    @cached_property
    def root(self):
        return utils.get_doc_root(self.release.lang, self.release.version)

    @cached_property
    def full_path(self):
        return utils.get_doc_path(self.root, self.path)

    @cached_property
    def body(self):
        """The document's body"""
        with open(str(self.full_path)) as fp:
            doc = json.load(fp)
        return doc['body']
