import re
from urllib.parse import quote

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.version import get_version_tuple
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from ..forms import DocSearchForm
from ..models import DocumentRelease
from ..search import START_SEL, STOP_SEL
from ..utils import get_doc_path, get_doc_root

register = template.Library()


@register.inclusion_tag("docs/search_form.html", takes_context=True)
def search_form(context):
    request = context["request"]
    release = DocumentRelease.objects.get_by_version_and_lang(
        context["version"],
        context["lang"],
    )
    return {
        "form": DocSearchForm(request.GET, release=release),
        "version": context["version"],
        "lang": context["lang"],
    }


@register.simple_tag(takes_context=True)
def get_all_doc_versions(context, url=None):
    """
    Get a list of all versions of this document to link to.

    Usage: {% get_all_doc_versions <url> as "varname" %}
    """
    lang = context.get("lang", "en")
    versions = []

    # Look for each version of the docs.
    for release in DocumentRelease.objects.select_related("release").filter(lang=lang):
        version_root = get_doc_root(release.lang, release.version)
        if version_root.exists():
            doc_path = get_doc_path(version_root, url)
            if doc_path:
                versions.append(release.version)

    # Save the versions into the context
    versions = sorted(get_version_tuple(x) for x in versions if x != "dev")
    return [".".join([str(part) for part in x]) for x in versions] + ["dev"]


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


@register.tag(name="pygment")
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
    nodelist = parser.parse(("endpygment",))
    parser.delete_first_token()
    return PygmentsNode(parser.compile_filter(tokens[1]), nodelist)


@register.filter(name="fragment")
@stringfilter
def generate_scroll_to_text_fragment(highlighted_text):
    """
    Given the highlighted text generated from Document.objects.search()
    constructs a scroll to text fragment.

    This will not work when:
    *  the highlighted test starts from a partial word, e.g it starts from
       test_environment rather than DiscoverRunner.setup_test_environment().
    *  it is trying to highlight a Python code snippet and the spacing logic
       has fallen down e.g. test = 5 not test=5 but test(a=5) not test(a = 5).
    """
    first_non_empty_line = next(
        (
            stripped
            for line in highlighted_text.split("\n")
            if (stripped := line.strip())
        ),
        "",
    )
    # Remove highlight tags and unwanted symbols.
    line_without_highlight = re.sub(
        rf"{START_SEL}|{STOP_SEL}|¶", "", first_non_empty_line
    )
    line_without_highlight = line_without_highlight.replace("&quot;", '"')
    # Remove excess spacing.
    single_spaced = re.sub(r"\s+", " ", line_without_highlight).strip()
    # Handle punctuation spacing.
    single_spaced = re.sub(r"\s([.,;:!?)(\]\[])", r"\1", single_spaced)
    # Due to Python code such as timezone.now(), remove the space after a bracket.
    single_spaced = re.sub(r"([(\[])\s", r"\1", single_spaced)
    return f"#:~:text={quote(single_spaced)}"
