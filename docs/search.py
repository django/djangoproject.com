# -*- coding: utf-8 -*-
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from elasticsearch.helpers import streaming_bulk
from elasticsearch_dsl import analysis, DocType, Long, Nested, Object, String
from elasticsearch_dsl.connections import connections

from .models import Document, document_url


class SearchPaginator(Paginator):
    """
    A better paginator for search results

    The normal Paginator does a .count() query and then a slice. Since ES
    results contain the total number of results, we can take an optimistic
    slice and then adjust the count.
    """
    def validate_number(self, number):
        """
        Validates the given 1-based page number.

        This class overrides the default behavior and ignores the upper bound.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        return number

    def page(self, number):
        """
        Returns a page object.

        This class overrides the default behavior and ignores "orphans" and
        assigns the count from the ES result to the Paginator.

        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page

        # Force the search to evaluate and then attach the count. We want to
        # avoid an extra useless query even if there are no results, so we
        # directly fetch the count from hits.
        result = self.object_list[bottom:top].execute()
        page = Page(result.hits, number, self)
        # Update the `_count`.
        self._count = page.object_list.total
        # Also store the aggregations, if any.
        if hasattr(result, 'aggregations'):
            page.aggregations = result.aggregations

        # Now that we have the count validate that the page number isn't higher
        # than the possible number of pages and adjust accordingly.
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return page


class ImprovedDocType(DocType):

    @classmethod
    def index_all(cls, using=None, delete=False, **kwargs):
        def actions_generator():
            for obj in cls.index_queryset().iterator():
                doc_dict = cls.from_django(obj).to_dict()
                doc_dict['_id'] = obj.id
                yield doc_dict

        client = connections.get_connection(using or cls._doc_type.using)
        if delete:
            client.indices.delete(index=cls._doc_type.index, ignore=[400, 404])
        cls._doc_type.init()
        for ok, item in streaming_bulk(client, actions_generator(),
                                       index=cls._doc_type.index,
                                       doc_type=cls._doc_type.name,
                                       raise_on_error=True,
                                       refresh=True,
                                       **kwargs):
            yield ok, item

    @classmethod
    def index_queryset(cls):
        return cls.model._default_manager.all()

    @classmethod
    def index_object(cls, obj):
        return cls.from_django(obj).save()

    @classmethod
    def unindex_object(cls, obj):
        return cls.get(id=obj.pk).delete()

    @classmethod
    def from_django(cls, obj):
        raise NotImplementedError('You must define a from_django classmethod '
                                  'to map ORM object fields to ES fields')


analysis.Tokenizer._builtins = analysis.TOKENIZERS = frozenset((
    'keyword', 'standard', 'path_hierarchy', 'whitespace'
))


class PathHierarchyTokenizer(analysis.Tokenizer):
    name = 'path_hierarchy'


class WhitespaceTokenizer(analysis.Tokenizer):
    name = 'whitespace'


path_analyzer = analysis.CustomAnalyzer('path',
                                        tokenizer='path_hierarchy',
                                        filter=['lowercase'])


lower_whitespace_analyzer = analysis.analyzer('lower_whitespace',
                                              tokenizer='whitespace',
                                              filter=['lowercase', 'stop'],
                                              char_filter=['html_strip'])


class DocumentDocType(ImprovedDocType):
    """
    The main documentation doc type to be used for searching.
    It stores a bit of meta data so we don't have to hit the db
    when rendering search results.

    The search view will be using the 'lang' and 'version' fields
    of the document's release to filter the search results, depending
    which was found in the URL.

    The breadcrumbs are shown under the search result title.
    """
    model = Document

    id = Long()
    title = String(analyzer=lower_whitespace_analyzer, boost=1.2)
    path = String(index='no', analyzer=path_analyzer)
    content = String(analyzer=lower_whitespace_analyzer)
    content_raw = String(index_options='offsets')
    release = Object(properties={
        'id': Long(),
        'version': String(index='not_analyzed'),
        'lang': String(index='not_analyzed'),
    })
    breadcrumbs = Nested(properties={
        'title': String(index='not_analyzed'),
        'path': String(index='not_analyzed'),
    })

    class Meta:
        index = 'docs'
        doc_type = 'document'

    @classmethod
    def index_queryset(cls):
        qs = super(DocumentDocType, cls).index_queryset()
        return (
            # don't index the module pages since source code is hard to
            # combine with full text search
            qs.exclude(path__startswith='_modules')
            # not the crazy big flattened index of the CBVs
              .exclude(path__startswith='ref/class-based-views/flattened-index')
              .select_related('release'))

    @classmethod
    def from_django(cls, obj):
        # turns HTML entities into unicode characters again and removes
        # all HTML tags, aka "plain text" versio of the document
        raw_body = strip_tags(unescape_entities(obj.body).replace(u'¶', ''))
        doc = cls(path=obj.path,
                  title=obj.title,
                  content=obj.body,
                  content_raw=raw_body,
                  meta={'id': obj.id})
        doc.release = {
            'id': obj.release.id,
            'lang': obj.release.lang,
            'version': obj.release.version,
        }
        breadcrumbs = []
        for breadcrumb in cls.model.objects.breadcrumbs(obj):
            breadcrumbs.append({
                'title': breadcrumb.title,
                'path': breadcrumb.path,
            })
        doc.breadcrumbs = breadcrumbs
        return doc

    def get_absolute_url(self):
        return document_url(self)
