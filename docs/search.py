from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.contrib.postgres.search import SearchVector
from django.db.models import Value
from django.db.models.functions import Coalesce

DOCUMENT_SEARCH_VECTOR = (
    SearchVector('title', weight='A') +
    SearchVector(Coalesce(KeyTextTransform('slug', 'metadata'), Value('')), weight='A') +
    SearchVector(Coalesce(KeyTextTransform('toc', 'metadata'), Value('')), weight='B') +
    SearchVector(Coalesce(KeyTextTransform('body', 'metadata'), Value('')), weight='C') +
    SearchVector(Coalesce(KeyTextTransform('parents', 'metadata'), Value('')), weight='D')
)
