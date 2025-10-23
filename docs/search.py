import requests
from django.contrib.postgres.search import SearchVector
from django.db.models import TextChoices
from django.db.models.fields.json import KeyTextTransform
from django.utils.translation import gettext_lazy as _

# Imported from
# https://github.com/postgres/postgres/blob/REL_14_STABLE/src/bin/initdb/initdb.c#L659
TSEARCH_CONFIG_LANGUAGES = {
    "ar": "arabic",
    "ca": "catalan",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "eu": "basque",
    "fi": "finnish",
    "fr": "french",
    "ga": "irish",
    "hi": "hindi",
    "hu": "hungarian",
    "hy": "armenian",
    "id": "indonesian",
    "it": "italian",
    "lt": "lithuanian",
    "ne": "nepali",
    "nl": "dutch",
    "no": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sr": "serbian",
    "sv": "swedish",
    "ta": "tamil",
    "tr": "turkish",
    "yi": "yiddish",
}

# Imported from
# https://github.com/postgres/postgres/blob/REL_14_STABLE/src/bin/initdb/initdb.c#L2557
DEFAULT_TEXT_SEARCH_CONFIG = "simple"


def get_document_search_vector(lang=DEFAULT_TEXT_SEARCH_CONFIG):
    """Return the search vector with the proper language config."""
    return (
        SearchVector("title", weight="A", config=lang)
        + SearchVector(KeyTextTransform("slug", "metadata"), weight="A", config=lang)
        + SearchVector(KeyTextTransform("toc", "metadata"), weight="B", config=lang)
        + SearchVector(KeyTextTransform("body", "metadata"), weight="C", config=lang)
        + SearchVector(KeyTextTransform("parents", "metadata"), weight="D", config=lang)
    )


START_SEL = "<mark>"
STOP_SEL = "</mark>"


class DocumentationCategory(TextChoices):
    """
    Categories used to filter the documentation search.
    The value must match a folder name within django/docs.
    """

    # Diátaxis folders.
    REFERENCE = "ref", _("API Reference")
    TOPICS = "topics", _("Using Django")
    HOWTO = "howto", _("How-to guides")
    RELEASE_NOTES = "releases", _("Release notes")
    WEBSITE = "website", _("Django Website")

    @classmethod
    def parse(cls, value, default=None):
        try:
            return cls(value)
        except ValueError:
            return None


def fetch_html(url, timeout=10):
    """
    Fetch the HTML of a page if status code is 200.
    Simulates a human browser and accepts only text/html.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
        ),
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers, timeout=timeout)

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            return response.text
        else:
            raise requests.RequestException(f"Unexpected Content-Type: {content_type}")
    else:
        raise requests.RequestException(
            f"Failed to fetch {url}, status code: {response.status_code}"
        )
