import datetime
import json
import operator
from functools import reduce
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import models, transaction
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from django_hosts.resolvers import reverse

from releases.models import Release

from . import utils


class DocumentReleaseManager(models.Manager):

    def current(self, lang='en'):
        current = self.get(is_default=True)
        if lang != 'en':
            try:
                return self.get(lang=lang, release=current.release)
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

    def by_version(self, version):
        return self.filter(**{'release__isnull': True} if version == 'dev' else {'release': version})

    def get_by_version_and_lang(self, version, lang):
        return self.by_version(version).get(lang=lang)

    def get_available_languages_by_version(self, version):
        return self.by_version(version).values_list('lang', flat=True)


class DocumentRelease(models.Model):
    """
    A "release" of documentation -- i.e. English for v1.2.
    """
    DEFAULT_CACHE_KEY = "%s_docs_version" % settings.CACHE_MIDDLEWARE_KEY_PREFIX

    lang = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    release = models.ForeignKey(
        Release,
        null=True,
        limit_choices_to={'status': 'f'},
        on_delete=models.CASCADE,
    )
    is_default = models.BooleanField(default=False)

    objects = DocumentReleaseManager()

    class Meta:
        unique_together = ('lang', 'release')

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
    def version(self):
        return 'dev' if self.release is None else self.release.version

    @property
    def human_version(self):
        """
        Return a "human readable" version of the version.
        """
        return "development" if self.release is None else self.release.version

    @property
    def is_dev(self):
        return self.release is None

    @property
    def is_supported(self):
        if self.release is None:
            return True
        latest_release = (Release.objects
                                 .filter(major=self.release.major,
                                         minor=self.release.minor,
                                         status='f')
                                 .order_by('-micro')
                                 .first())
        if latest_release is None:
            return True
        eol_date = latest_release.eol_date
        return eol_date is None or eol_date > datetime.date.today()

    @property
    def scm_url(self):
        url = 'git://github.com/django/django.git'
        if not self.is_dev:
            url += '@stable/' + self.version + '.x'
        return url

    @transaction.atomic
    def sync_to_db(self, decoded_documents):
        """
        Sync the given list of documents (decoded fjson files from sphinx) to
        the database. Deletes all the release's documents first then
        reinserts them as needed.
        """
        self.documents.all().delete()

        for document in decoded_documents:
            if 'body' not in document or 'title' not in document:
                # We don't care about indexing documents with no body or title
                continue

            Document.objects.create(
                release=self,
                path=_clean_document_path(document['current_page_name']),
                title=unescape_entities(strip_tags(document['title'])),
            )


def _clean_document_path(path):
    # We have to be a bit careful to reverse-engineer the correct
    # relative path component, especially for "index" documents,
    # otherwise the search results will be incorrect.
    if path.endswith('/index'):
        path = path[:-6]

    return path


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

    def breadcrumbs(self, document):
        # get an ascending list of parent paths except the root path ('.')
        parent_paths = list(Path(document.path).parents)[:-1]
        if parent_paths:
            or_queries = [models.Q(path=str(path)) for path in parent_paths]
            return (self.filter(reduce(operator.or_, or_queries))
                        .filter(release=document.release)
                        .exclude(pk=document.pk)
                        .order_by('path'))
        else:
            return self.none()


class Document(models.Model):
    """
    An individual document. Used mainly as a hook point for the search.
    """
    release = models.ForeignKey(
        DocumentRelease,
        related_name='documents',
        on_delete=models.CASCADE,
     )
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
