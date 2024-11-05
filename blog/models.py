from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import caches
from django.db import models
from django.test import RequestFactory
from django.utils import timezone
from django.utils.cache import _generate_cache_header_key
from django.utils.translation import gettext_lazy as _
from django_hosts.resolvers import reverse
from docutils.core import publish_parts
from markdown import markdown
from markdown.extensions.toc import TocExtension, slugify as _md_title_slugify

BLOG_DOCUTILS_SETTINGS = {
    "doctitle_xform": False,
    "initial_header_level": 3,
    "id_prefix": "s-",
    "raw_enabled": False,
    "file_insertion_enabled": False,
}
BLOG_DOCUTILS_SETTINGS.update(getattr(settings, "BLOG_DOCUTILS_SETTINGS", {}))


def _md_slugify(value, separator):
    # matches the `id_prefix` setting of BLOG_DOCUTILS_SETTINGS
    return "s" + separator + _md_title_slugify(value, separator)


class EntryQuerySet(models.QuerySet):
    def published(self):
        return self.active().filter(pub_date__lte=timezone.now())

    def active(self):
        return self.filter(is_active=True)


class ContentFormat(models.TextChoices):
    REST = "reST", "reStructuredText"
    HTML = "html", "Raw HTML"
    MARKDOWN = "md", "Markdown"

    @classmethod
    def to_html(cls, fmt, source):
        """
        Convert the given source from the given format to HTML
        """
        if not fmt or fmt == cls.HTML:
            return source
        if fmt == cls.REST:
            return publish_parts(
                source=source,
                writer_name="html",
                settings_overrides=BLOG_DOCUTILS_SETTINGS,
            )["fragment"]
        if fmt == cls.MARKDOWN:
            return markdown(
                source,
                output_format="html",
                extensions=[
                    # baselevel matches `initial_header_level` from BLOG_DOCUTILS_SETTINGS
                    TocExtension(baselevel=3, slugify=_md_slugify),
                ],
            )
        raise ValueError(f"Unsupported format {fmt}")


class Entry(models.Model):
    headline = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date="pub_date")
    is_active = models.BooleanField(
        help_text=_(
            "Tick to make this entry live (see also the publication date). "
            "Note that administrators (like yourself) are allowed to preview "
            "inactive entries whereas the general public aren't."
        ),
        default=False,
    )
    pub_date = models.DateTimeField(
        verbose_name=_("Publication date"),
        help_text=_(
            "For an entry to be published, it must be active and its "
            "publication date must be in the past."
        ),
    )
    content_format = models.CharField(choices=ContentFormat, max_length=50)
    summary = models.TextField()
    summary_html = models.TextField()
    body = models.TextField()
    body_html = models.TextField()
    author = models.CharField(max_length=100)

    objects = EntryQuerySet.as_manager()

    class Meta:
        db_table = "blog_entries"
        verbose_name_plural = "entries"
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        kwargs = {
            "year": self.pub_date.year,
            "month": self.pub_date.strftime("%b").lower(),
            "day": self.pub_date.strftime("%d").lower(),
            "slug": self.slug,
        }
        return reverse("weblog:entry", kwargs=kwargs)

    def is_published(self):
        """
        Return True if the entry is publicly accessible.
        """
        return self.is_active and self.pub_date <= timezone.now()

    is_published.boolean = True

    def save(self, *args, **kwargs):
        self.summary_html = ContentFormat.to_html(self.content_format, self.summary)
        self.body_html = ContentFormat.to_html(self.content_format, self.body)
        super().save(*args, **kwargs)
        self.invalidate_cached_entry()

    def invalidate_cached_entry(self):
        url = urlparse(self.get_absolute_url())
        rf = RequestFactory(
            SERVER_NAME=url.netloc,
            HTTP_X_FORWARDED_PROTOCOL=url.scheme,
        )
        is_secure = url.scheme == "https"
        request = rf.get(url.path, secure=is_secure)
        request.LANGUAGE_CODE = "en"
        cache = caches[settings.CACHE_MIDDLEWARE_ALIAS]
        cache_key = _generate_cache_header_key(
            settings.CACHE_MIDDLEWARE_KEY_PREFIX, request
        )
        cache.delete(cache_key)


class EventQuerySet(EntryQuerySet):
    def past(self):
        return self.filter(date__lte=timezone.now()).order_by("-date")

    def future(self):
        return self.filter(date__gte=timezone.now()).order_by("date")


class Event(models.Model):
    headline = models.CharField(max_length=200, null=False)
    external_url = models.URLField()
    date = models.DateField()
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(
        help_text=_(
            "Tick to make this event live (see also the publication date). "
            "Note that administrators (like yourself) are allowed to preview "
            "inactive events whereas the general public aren't."
        ),
        default=False,
    )
    pub_date = models.DateTimeField(
        verbose_name=_("Publication date"),
        help_text=_(
            "For an event to be published, it must be active and its "
            "publication date must be in the past."
        ),
    )

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"

    def is_published(self):
        """
        Return True if the event is publicly accessible.
        """
        return self.is_active and self.pub_date <= timezone.now()

    is_published.boolean = True
