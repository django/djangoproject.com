from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.search import SearchVector
from django.db.models import F

# Imported from https://github.com/postgres/postgres/blob/REL_10_STABLE/src/bin/initdb/initdb.c#L664
TSEARCH_CONFIG_LANGUAGES = {
    'da': 'danish',
    'de': 'german',
    'en': 'english',
    'es': 'spanish',
    'fi': 'finnish',
    'fr': 'french',
    'hu': 'hungarian',
    'it': 'italian',
    'nl': 'dutch',
    'no': 'norwegian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'sv': 'swedish',
    'tr': 'turkish',
}
# Imported from https://github.com/postgres/postgres/blob/REL_10_STABLE/src/bin/initdb/initdb.c#L2599
DEFAULT_TEXT_SEARCH_CONFIG = 'simple'

DOCUMENT_SEARCH_VECTOR = (
    SearchVector('title', weight='A', config=F('config')) +
    SearchVector(KeyTextTransform('slug', 'metadata'), weight='A', config=F('config')) +
    SearchVector(KeyTextTransform('toc', 'metadata'), weight='B', config=F('config')) +
    SearchVector(KeyTextTransform('body', 'metadata'), weight='C', config=F('config')) +
    SearchVector(KeyTextTransform('parents', 'metadata'), weight='D', config=F('config'))
)
