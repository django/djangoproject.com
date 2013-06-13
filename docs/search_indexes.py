# -*- coding: utf-8 -*-

import json
from django.utils.html import strip_tags
import haystack
import haystack.indexes
from . import utils
from .models import Document

class DocumentIndex(haystack.indexes.SearchIndex):
    text = haystack.indexes.CharField(document=True)
    lang = haystack.indexes.CharField(model_attr='release__lang', faceted=True)
    version = haystack.indexes.CharField(model_attr='release__version', faceted=True)
    path = haystack.indexes.CharField(model_attr='path')
    title = haystack.indexes.CharField(model_attr='title')

    def get_queryset(self):
        return Document.objects.all().select_related('release')

    def prepare_text(self, obj):
        root = utils.get_doc_root(obj.release.lang, obj.release.version)
        docpath = utils.get_doc_path(root, obj.path)
        with open(docpath) as fp:
            doc = json.load(fp)
        return strip_tags(doc['body']).replace(u'¶', '')

haystack.site.register(Document, DocumentIndex)
