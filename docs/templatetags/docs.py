from distutils.version import StrictVersion

from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from ..forms import DocSearchForm
from ..models import DocumentRelease
from ..utils import get_doc_path, get_doc_root

register = template.Library()


@register.inclusion_tag('docs/search_form.html', takes_context=True)
def search_form(context):
    request = context['request']
    release = DocumentRelease.objects.get_by_version_and_lang(
        context['version'],
        context['lang'],
    )
    return {
        'form': DocSearchForm(request.GET, release=release),
        'version': context['version'],
        'lang': context['lang'],
    }


@register.simple_tag(takes_context=True)
def get_all_doc_versions(context, url=None):
    """
    Get a list of all versions of this document to link to.

    Usage: {% get_all_doc_versions <url> as "varname" %}
    """
    lang = context.get('lang', 'en')
    versions = []

    # Look for each version of the docs.
    for release in DocumentRelease.objects.filter(lang=lang):
        version_root = get_doc_root(release.lang, release.version)
        if version_root.exists():
            doc_path = get_doc_path(version_root, url)
            if doc_path:
                versions.append(release.version)

    # Save the versions into the context
    versions = sorted(StrictVersion(x) for x in versions if x != 'dev')
    return [str(x) for x in versions] + ['dev']


class PygmentsNode(template.Node):

    def __init__(self, lexer_name, nodelist):
        self.nodelist = nodelist
        self.lexer_name = lexer_name

    def render(self, context):
        content = self.nodelist.render(context)
        lexer_name = self.lexer_name.resolve(context)
        lexer = get_lexer_by_name(lexer_name)
        output = highlight(content, lexer, HtmlFormatter())
        return mark_safe(output)


@register.tag(name='pygment')
def do_pygments(parser, token):
    """
    Template tag that uses pygments to highlight code examples.

    Example usage:

        {% pygment 'python' %}
        def view_article(request, pk):
            return render(request, 'view_article.html', {
                'article_id': get_object_or_404(Article, pk=pk)
            })
        {% endpygment %}

    """
    tokens = token.split_contents()
    nodelist = parser.parse(('endpygment',))
    parser.delete_first_token()
    return PygmentsNode(parser.compile_filter(tokens[1]), nodelist)
