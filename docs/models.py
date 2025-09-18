import datetime
import html
import json
import operator
from functools import partial, reduce
from pathlib import Path

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVectorField,
    TrigramSimilarity,
)
from django.core.cache import cache
from django.db import models, transaction
from django.db.models import (
    Case,
    Q,
    When,
)
from django.db.models.fields.json import KeyTextTransform
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django_hosts.resolvers import reverse

from releases.models import Release

from . import utils
from .search import (
    DEFAULT_TEXT_SEARCH_CONFIG,
    START_SEL,
    STOP_SEL,
    TSEARCH_CONFIG_LANGUAGES,
    get_document_search_vector,
)


class DocumentReleaseQuerySet(models.QuerySet):
    def current(self, lang="en"):
        current = self.get(is_default=True)
        if lang != "en":
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
                current_version = "dev"
            cache.set(
                DocumentRelease.DEFAULT_CACHE_KEY,
                current_version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        return current_version

    def _by_version_Q(self, version):
        return (
            models.Q(release__isnull=True)
            if version == "dev"
            else models.Q(release=version)
        )

    def by_version(self, version):
        return self.filter(self._by_version_Q(version))

    def by_versions(self, *versions):
        if not versions:
            raise ValueError("by_versions() takes at least one argument")
        return self.filter(reduce(operator.or_, map(self._by_version_Q, versions)))

    def get_by_version_and_lang(self, version, lang):
        return self.by_version(version).get(lang=lang)

    def get_available_languages_by_version(self, version):
        return self.by_version(version).values_list("lang", flat=True).order_by("lang")


class DocumentRelease(models.Model):
    """
    A "release" of documentation -- i.e. English for v1.2.
    """

    DEFAULT_CACHE_KEY = "%s_docs_version" % settings.CACHE_MIDDLEWARE_KEY_PREFIX

    lang = models.CharField(max_length=7, choices=settings.LANGUAGES, default="en")
    release = models.ForeignKey(
        Release,
        null=True,
        limit_choices_to={"status": "f"},
        on_delete=models.CASCADE,
    )
    is_default = models.BooleanField(default=False)

    objects = DocumentReleaseQuerySet.as_manager()

    class Meta:
        unique_together = ("lang", "release")

    def __str__(self):
        return f"{self.lang}/{self.version}"

    def get_absolute_url(self):
        kwargs = {
            "lang": self.lang,
            "version": self.version,
        }
        return reverse("document-index", host="docs", kwargs=kwargs)

    def save(self, *args, **kwargs):
        # There can be only one. Default, that is.
        if self.is_default:
            DocumentRelease.objects.update(is_default=False)
            cache.set(
                self.DEFAULT_CACHE_KEY,
                self.version,
                settings.CACHE_MIDDLEWARE_SECONDS,
            )
        super().save(*args, **kwargs)

    @property
    def version(self):
        return "dev" if self.release is None else self.release.version

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
    def is_preview(self):
        return not self.is_dev and self.release.date is None

    @property
    def is_supported(self):
        if self.release is None:
            return True
        latest_release = (
            Release.objects.filter(
                major=self.release.major, minor=self.release.minor, status="f"
            )
            .order_by("-micro")
            .first()
        )
        if latest_release is None:
            return True
        eol_date = latest_release.eol_date
        return eol_date is None or eol_date > datetime.date.today()

    @property
    def scm_url(self):
        url = "https://github.com/django/django.git"
        if not self.is_dev:
            url += "@stable/" + self.version + ".x"
        return url

    @transaction.atomic
    def sync_to_db(self, decoded_documents):
        """
        Sync the given list of documents (decoded fjson files from sphinx) to
        the database. Deletes all the release's documents first then
        reinserts them as needed.
        """
        self.documents.all().delete()

        # Read excluded paths from robots.docs.txt.
        robots_path = settings.BASE_DIR.joinpath(
            "djangoproject", "static", "robots.docs.txt"
        )
        with open(str(robots_path)) as fh:
            excluded_paths = [
                line.strip().split("/")[-1]
                for line in fh
                if line.startswith(f"Disallow: /{self.lang}/{self.release_id}/")
            ]

        for document in decoded_documents:
            if (
                "body" not in document
                or "title" not in document
                or document["current_page_name"].split("/")[0] in excluded_paths
            ):
                # We don't care about indexing documents with no body or title,
                # or partially translated
                continue

            document_path = _clean_document_path(document["current_page_name"])
            document["slug"] = Path(document_path).parts[-1]
            document["parents"] = " ".join(Path(document_path).parts[:-1])
            Document.objects.create(
                release=self,
                path=document_path,
                title=html.unescape(strip_tags(document["title"])),
                metadata=document,
                config=TSEARCH_CONFIG_LANGUAGES.get(
                    self.lang[:2], DEFAULT_TEXT_SEARCH_CONFIG
                ),
            )
        for document in self.documents.all():
            document.metadata["breadcrumbs"] = list(
                Document.objects.breadcrumbs(document).values("title", "path")
            )
            document.save(update_fields=("metadata",))


def _clean_document_path(path):
    # We have to be a bit careful to reverse-engineer the correct
    # relative path component, especially for "index" documents,
    # otherwise the search results will be incorrect.
    if path.endswith("/index"):
        path = path[:-6]

    return path


def document_url(doc):
    if doc.path:
        kwargs = {
            "lang": doc.release.lang,
            "version": doc.release.version,
            "url": doc.path,
        }
        return reverse("document-detail", host="docs", kwargs=kwargs)
    else:
        kwargs = {
            "lang": doc.release.lang,
            "version": doc.release.version,
        }
        return reverse("document-index", host="docs", kwargs=kwargs)


class DocumentQuerySet(models.QuerySet):
    def breadcrumbs(self, document):
        # get an ascending list of parent paths except the root path ('.')
        parent_paths = list(Path(document.path).parents)[:-1]
        if parent_paths:
            or_queries = [models.Q(path=str(path)) for path in parent_paths]
            return (
                self.filter(reduce(operator.or_, or_queries))
                .filter(release_id=document.release_id)
                .exclude(pk=document.pk)
                .order_by("path")
            )
        else:
            return self.none()

    def search(self, query_text, release, document_category=None):
        """Use full-text search to return documents matching query_text."""
        query_text = query_text.strip()
        if query_text:
            search_query = SearchQuery(
                query_text, config=models.F("config"), search_type="websearch"
            )
            search_rank = SearchRank(models.F("search_vector"), search_query)
            search = partial(
                SearchHeadline,
                start_sel=START_SEL,
                stop_sel=STOP_SEL,
                config=models.F("config"),
            )
            base_filter = Q(release_id=release.id)
            if document_category:
                base_filter &= Q(metadata__parents__startswith=document_category)
            base_qs = (
                self.select_related("release__release")
                .filter(base_filter)
                .annotate(
                    headline=search("title", search_query),
                    highlight=search(
                        KeyTextTransform("body", "metadata"),
                        search_query,
                    ),
                    searched_python_objects=search(
                        KeyTextTransform("python_objects_search", "metadata"),
                        search_query,
                        highlight_all=True,
                    ),
                    breadcrumbs=models.F("metadata__breadcrumbs"),
                    python_objects=models.F("metadata__python_objects"),
                )
                .only(
                    "path",
                    "release__lang",
                    "release__release__version",
                )
            )
            vector_qs = (
                base_qs.alias(rank=search_rank)
                .filter(search_vector=search_query)
                .order_by("-rank")
            )
            if not vector_qs:
                return (
                    base_qs.alias(
                        similarity=TrigramSimilarity(
                            "title", utils.sanitize_for_trigram(query_text)
                        )
                    )
                    .filter(similarity__gt=0.3)
                    .order_by("-similarity")
                )
            else:
                return vector_qs
        else:
            return self.none()


class Document(models.Model):
    """
    An individual document. Used mainly as a hook point for the search.
    """

    release = models.ForeignKey(
        DocumentRelease,
        related_name="documents",
        on_delete=models.CASCADE,
    )
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    metadata = models.JSONField(default=dict)
    # Use Case/When to force the expression to be immutable, per:
    # https://www.paulox.net/2025/09/08/djangocon-us-2025/
    search_vector = models.GeneratedField(
        expression=Case(
            *[
                When(config=lang, then=get_document_search_vector(lang))
                for lang in TSEARCH_CONFIG_LANGUAGES.values()
            ],
            default=get_document_search_vector(),
        ),
        output_field=SearchVectorField(),
        db_persist=True,
    )
    config = models.SlugField(
        db_default=DEFAULT_TEXT_SEARCH_CONFIG, default=DEFAULT_TEXT_SEARCH_CONFIG
    )

    objects = DocumentQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    config__in=[
                        DEFAULT_TEXT_SEARCH_CONFIG,
                        *TSEARCH_CONFIG_LANGUAGES.values(),
                    ]
                ),
                name="document_config_allowed_languages",
            )
        ]
        indexes = [
            models.Index(
                fields=["release", "title"], name="document_release_title_idx"
            ),
            GinIndex(fields=["search_vector"], name="document_search_vector_idx"),
        ]
        unique_together = ("release", "path")

    def __str__(self):
        return "/".join([self.release.lang, self.release.version, self.path])

    def get_absolute_url(self):
        return document_url(self)

    @cached_property
    def content_raw(self):
        return strip_tags(html.unescape(self.metadata["content"]).replace("¶", ""))

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
        return doc["body"]
