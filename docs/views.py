import datetime
import json

from django.conf import settings
from django.core.paginator import InvalidPage
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _, activate
from django.views import static
from django.views.decorators.cache import cache_page

from django_hosts.resolvers import reverse

from elasticsearch_dsl import query

from .forms import DocSearchForm
from .models import DocumentRelease, Document
from .search import DocumentDocType, SearchPaginator
from .utils import get_doc_root_or_404, get_doc_path_or_404


CURRENT_LTS = '1.4'
UNSUPPORTED_THRESHOLD = '1.7'
SIMPLE_SEARCH_OPERATORS = ['+', '|', '-', '"', '*', '(', ')', '~']


def version_is_unsupported(version):
    # TODO: would be nice not to hardcode this.
    return version != CURRENT_LTS and version < UNSUPPORTED_THRESHOLD


def index(request):
    return redirect(DocumentRelease.objects.current())


def language(request, lang):
    return redirect(DocumentRelease.objects.current(lang))


def stable(request, lang, version, url):
    path = request.get_full_path()
    current_version = DocumentRelease.objects.current_version()
    return redirect(path.replace(version, current_version, 1))


def document(request, lang, version, url):
    # If either of these can't be encoded as ascii then later on down the line an
    # exception will be emitted by unipath, proactively check for bad data (mostly
    # from the Googlebot) so we can give a nice 404 error.
    try:
        version.encode("ascii")
        url.encode("ascii")
    except UnicodeEncodeError:
        raise Http404

    if lang != 'en':
        activate(lang)

    docroot = get_doc_root_or_404(lang, version)
    doc_path = get_doc_path_or_404(docroot, url)

    if version == 'dev':
        rtd_version = 'latest'
    elif version >= '1.5':
        rtd_version = version + '.x'
    else:
        rtd_version = version + '.X'

    template_names = [
        'docs/%s.html' % str(doc_path.relative_to(docroot)).replace(str(doc_path.suffix), ''),
        'docs/doc.html',
    ]

    context = {
        'doc': json.load(doc_path.open('r')),
        'env': json.load((docroot.joinpath('globalcontext.json')).open('r')),
        'lang': lang,
        'version': version,
        'version_is_dev': version == 'dev',
        'version_is_unsupported': version_is_unsupported(version),
        'rtd_version': rtd_version,
        'docurl': url,
        'update_date': datetime.datetime.fromtimestamp((docroot.joinpath('last_build')).stat().st_mtime),
        'redirect_from': request.GET.get('from', None),
    }
    return render(request, template_names, context)


def pot_file(request, pot_name):
    version = DocumentRelease.objects.current().version
    doc_root = get_doc_root_or_404('en', version, subroot='gettext')
    return static.serve(request, document_root=doc_root, path=pot_name)


def sphinx_static(request, lang, version, path, subpath=None):
    """
    Serve Sphinx static assets from a subdir of the build location.
    """
    document_root = get_doc_root_or_404(lang, version).joinpath(subpath)
    return static.serve(request, document_root=document_root, path=path)


def objects_inventory(request, lang, version):
    response = static.serve(request,
                            document_root=get_doc_root_or_404(lang, version),
                            path="objects.inv")
    response['Content-Type'] = "text/plain"
    return response


def redirect_index(request, *args, **kwargs):
    assert request.path.endswith('index/')
    return redirect(request.path[:-6])


def redirect_search(request):
    """
    Legacy search view to handle old queries correctly, e.g. in scraping
    sites, command line interface etc.
    """
    release = DocumentRelease.objects.current()
    kwargs = {
        'lang': release.lang,
        'version': release.version,
    }
    search_url = reverse('document-search', host='docs', kwargs=kwargs)
    q = request.GET.get('q') or None
    if q:
        search_url += '?q=%s' % q
    return redirect(search_url)


def search_results(request, lang, version, per_page=10, orphans=3):
    """
    Search view to handle language and version specific queries.
    The old search view is being redirected here.
    """
    release = get_object_or_404(DocumentRelease, version=version, lang=lang)
    form = DocSearchForm(request.GET or None, release=release)

    context = {
        'form': form,
        'lang': release.lang,
        'version': release.version,
        'release': release,
        'searchparams': request.GET.urlencode(),
        'version_is_dev': version == 'dev',
        'version_is_unsupported': version_is_unsupported(version),
    }

    if form.is_valid():
        q = form.cleaned_data.get('q')

        if q:
            # catch queries that are coming from browser search bars
            exact = (DocumentDocType.index_queryset()
                                    .filter(release=release, title=q)
                                    .first())
            if exact is not None:
                return redirect(exact)

            should = []
            if any(operator in q for operator in SIMPLE_SEARCH_OPERATORS):
                should.append(query.SimpleQueryString(fields=['title',
                                                              'content^5'],
                                                      query=q,
                                                      analyzer='stop',
                                                      default_operator='and'))
            else:
                # let's just use simple queries since they allow some
                # neat syntaxes for exclusion etc. For more info see
                # http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html
                should = [query.MultiMatch(fields=['title^10', 'content'],
                                           query=q,
                                           type='phrase_prefix'),
                          query.Match(query=q),
                          query.MultiMatch(fields=['title^5', 'content'],
                                           query=q,
                                           fuzziness=1)]

            # then apply the queries and filter out anything not matching
            # the wanted version and language, also highlight the content
            # and order the highlighted snippets by score so that the most
            # fitting result is used
            results = (DocumentDocType.search()
                                      .query(query.Bool(should=should))
                                      .filter('term', release__lang=release.lang)
                                      .filter('term', release__version=release.version)
                                      .highlight_options(order='score')
                                      .highlight('content'))

            page_number = request.GET.get('page') or 1
            paginator = SearchPaginator(results, per_page=per_page, orphans=orphans)

            try:
                page_number = int(page_number)
            except ValueError:
                if page_number == 'last':
                    page_number = paginator.num_pages
                else:
                    raise Http404(_("Page is not 'last', "
                                    "nor can it be converted to an int."))

            try:
                page = paginator.page(page_number)
            except InvalidPage as e:
                raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                    'page_number': page_number,
                    'message': str(e)
                })

            context.update({
                'query': q,
                'page': page,
                'paginator': paginator,
            })

    if release.lang != 'en':
        activate(release.lang)

    return render(request, 'docs/search_results.html', context)


def search_suggestions(request, lang, version, per_page=20):
    """
    The endpoint for the OpenSearch browser integration.

    This will do a simple prefix match against the title to catch
    documents with a meaningful title.

    The link list contains redirect URLs so that IE will correctly
    redirect to those documents.
    """
    release = get_object_or_404(DocumentRelease, version=version, lang=lang)

    form = DocSearchForm(request.GET or None, release=release)
    suggestions = []

    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            search = DocumentDocType.search()
            search = (search.query(query.SimpleQueryString(fields=['title^10',
                                                                   'content'],
                                                           query=q,
                                                           analyzer='stop',
                                                           default_operator='and'))
                            .filter('term', release__lang=release.lang)
                            .filter('term', release__version=release.version)
                            .fields(['title', '_source']))

            suggestions.append(q)
            titles = []
            links = []
            content_type = ContentType.objects.get_for_model(Document)
            results = search[0:per_page].execute()
            for result in results:
                titles.append(result.title)
                kwargs = {
                    'content_type_id': content_type.pk,
                    'object_id': result.meta.id,
                }
                links.append(reverse('django.contrib.contenttypes.views.shortcut',
                                     kwargs=kwargs))
            suggestions.append(titles)
            suggestions.append([])
            suggestions.append(links)

    return JsonResponse(suggestions, safe=False)

if not settings.DEBUG:
    # 1 hour to handle the many requests
    search_suggestions = cache_page(60 * 60)(search_suggestions)


def search_description(request, lang, version):
    """
    Render an OpenSearch description.
    """
    release = get_object_or_404(DocumentRelease, version=version, lang=lang)
    context = {
        'site': Site.objects.get_current(),
        'release': release,
    }
    return render(request, 'docs/search_description.xml', context,
                  content_type='application/opensearchdescription+xml')

if not settings.DEBUG:
    # 1 week because there is no need to render it more often
    search_description = cache_page(60 * 60 * 24 * 7)(search_description)
