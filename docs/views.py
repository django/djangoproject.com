import datetime
import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps.views import x_robots_tag
from django.contrib.sites.models import Site
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils.translation import activate, gettext_lazy as _
from django.views import static
from django.views.decorators.cache import cache_page
from django_hosts.resolvers import reverse

from .forms import DocSearchForm
from .models import Document, DocumentRelease
from .utils import get_doc_path_or_404, get_doc_root_or_404

SIMPLE_SEARCH_OPERATORS = ['+', '|', '-', '"', '*', '(', ')', '~']


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
        lang.encode("ascii")
        version.encode("ascii")
        url.encode("ascii")
    except UnicodeEncodeError:
        raise Http404

    activate(lang)

    canonical_version = DocumentRelease.objects.current_version()
    canonical = version == canonical_version
    if version == 'stable':
        version = canonical_version

    docroot = get_doc_root_or_404(lang, version)
    doc_path = get_doc_path_or_404(docroot, url)
    try:
        release = DocumentRelease.objects.get_by_version_and_lang(version, lang)
    except DocumentRelease.DoesNotExist:
        raise Http404

    if version == 'dev':
        rtd_version = 'latest'
    else:
        rtd_version = version + '.x'

    template_names = [
        'docs/%s.html' % str(doc_path.relative_to(docroot)).replace(str(doc_path.suffix), ''),
        'docs/doc.html',
    ]

    def load_json_file(path):
        with path.open('r') as f:
            return json.load(f)

    context = {
        'doc': load_json_file(doc_path),
        'env': load_json_file(docroot.joinpath('globalcontext.json')),
        'lang': lang,
        'version': version,
        'canonical_version': canonical_version,
        'canonical': canonical,
        'available_languages': DocumentRelease.objects.get_available_languages_by_version(version),
        'release': release,
        'rtd_version': rtd_version,
        'docurl': url,
        'update_date': datetime.datetime.fromtimestamp((docroot.joinpath('last_build')).stat().st_mtime),
        'redirect_from': request.GET.get('from', None),
    }
    response = render(request, template_names, context)
    # Tell Fastly to re-fetch from the origin once a week (we'll invalidate the cache sooner if needed)
    response['Surrogate-Control'] = 'max-age=%d' % (7 * 24 * 60 * 60)
    return response


if not settings.DEBUG:
    # Specify a dedicated cache for docs pages that need to be purged after docs rebuilds
    # (see docs/management/commands/update_docs.py):
    document = cache_page(settings.CACHE_MIDDLEWARE_SECONDS, cache='docs-pages')(document)


def pot_file(request, pot_name):
    version = DocumentRelease.objects.current().version
    doc_root = str(get_doc_root_or_404('en', version, subroot='gettext'))
    return static.serve(request, document_root=doc_root, path=pot_name)


def sphinx_static(request, lang, version, path, subpath=None):
    """
    Serve Sphinx static assets from a subdir of the build location.
    """
    document_root = str(get_doc_root_or_404(lang, version).joinpath(subpath))
    return static.serve(request, document_root=document_root, path=path)


def objects_inventory(request, lang, version):
    response = static.serve(request,
                            document_root=str(get_doc_root_or_404(lang, version)),
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
    try:
        release = DocumentRelease.objects.get_by_version_and_lang(version, lang)
    except DocumentRelease.DoesNotExist:
        raise Http404

    activate(lang)

    form = DocSearchForm(request.GET or None, release=release)

    context = {
        'form': form,
        'lang': release.lang,
        'version': release.version,
        'release': release,
        'searchparams': request.GET.urlencode(),
    }

    if form.is_valid():
        q = form.cleaned_data.get('q')

        if q:
            # catch queries that are coming from browser search bars
            exact = Document.objects.filter(release=release, title=q).first()
            if exact is not None:
                return redirect(exact)

            results = Document.objects.search(q, release)

            page_number = request.GET.get('page') or 1
            paginator = Paginator(results, per_page=per_page, orphans=orphans)

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

    return render(request, 'docs/search_results.html', context)


def search_suggestions(request, lang, version, per_page=20):
    """
    The endpoint for the OpenSearch browser integration.

    This will do a simple prefix match against the title to catch
    documents with a meaningful title.

    The link list contains redirect URLs so that IE will correctly
    redirect to those documents.
    """
    try:
        release = DocumentRelease.objects.get_by_version_and_lang(version, lang)
    except DocumentRelease.DoesNotExist:
        raise Http404

    activate(lang)

    form = DocSearchForm(request.GET or None, release=release)
    suggestions = []

    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            results = Document.objects.filter(
                release__lang=release.lang,
            ).filter(
                release__release__version=release.version,
            ).filter(
                title__contains=q,
            )
            suggestions.append(q)
            titles = []
            links = []
            content_type = ContentType.objects.get_for_model(Document)
            for result in results:
                titles.append(result.title)
                kwargs = {
                    'content_type_id': content_type.pk,
                    'object_id': result.id,
                }
                links.append(reverse('contenttypes-shortcut', kwargs=kwargs))
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
    try:
        release = DocumentRelease.objects.get_by_version_and_lang(version, lang)
    except DocumentRelease.DoesNotExist:
        raise Http404

    activate(lang)

    context = {
        'site': Site.objects.get_current(),
        'release': release,
    }
    return render(request, 'docs/search_description.xml', context,
                  content_type='application/opensearchdescription+xml')


if not settings.DEBUG:
    # 1 week because there is no need to render it more often
    search_description = cache_page(60 * 60 * 24 * 7)(search_description)


@x_robots_tag
def sitemap_index(request, sitemaps):
    """
    Simplified version of django.contrib.sitemaps.views.index that uses
    django_hosts for URL reversing.
    """
    sites = []
    for section in sitemaps.keys():
        sitemap_url = reverse('document-sitemap', host='docs', kwargs={'section': section})
        sites.append(sitemap_url)
    return TemplateResponse(
        request,
        'sitemap_index.xml',
        {'sitemaps': sites},
        content_type='application/xml',
    )
