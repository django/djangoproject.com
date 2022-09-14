from django.contrib.postgres.search import SearchVector
from django.db.models import F
from django.db.models.fields.json import KeyTextTransform

# Imported from https://github.com/postgres/postgres/blob/REL_12_STABLE/src/bin/initdb/initdb.c#L701
TSEARCH_CONFIG_LANGUAGES = {
    'ar': 'arabic',
    'da': 'danish',
    'de': 'german',
    'en': 'english',
    'es': 'spanish',
    'fi': 'finnish',
    'fr': 'french',
    'ga': 'irish',
    'hu': 'hungarian',
    'id': 'indonesian',
    'it': 'italian',
    'lt': 'lithuanian',
    'ne': 'nepali',
    'nl': 'dutch',
    'no': 'norwegian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'sv': 'swedish',
    'ta': 'tamil',
    'tr': 'turkish',
}

# Imported from https://github.com/postgres/postgres/blob/REL_12_STABLE/src/bin/initdb/initdb.c#L2668
DEFAULT_TEXT_SEARCH_CONFIG = 'simple'

DOCUMENT_SEARCH_VECTOR = (
    SearchVector('title', weight='A', config=F('config')) +
    SearchVector(KeyTextTransform('slug', 'metadata'), weight='A', config=F('config')) +
    SearchVector(KeyTextTransform('toc', 'metadata'), weight='B', config=F('config')) +
    SearchVector(KeyTextTransform('body', 'metadata'), weight='C', config=F('config')) +
    SearchVector(KeyTextTransform('parents', 'metadata'), weight='D', config=F('config'))
)
