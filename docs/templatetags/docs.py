from django import template
from ..forms import DocSearchForm
from ..models import DocumentRelease
from ..utils import get_doc_root, get_doc_path

register = template.Library()


@register.inclusion_tag('docs/search_form.html', takes_context=True)
def search_form(context, search_form_id='sidebar_search'):
    request = context['request']
    auto_id = 'id_%s_%%s' % search_form_id
    release = DocumentRelease.objects.get(version=context['version'], lang=context['lang'])
    return {
        'form': DocSearchForm(request.GET, auto_id=auto_id, default_release=release),
        'search_form_id': search_form_id,
    }


@register.tag
def get_all_doc_versions(parser, token):
    """
    Get a list of all versions of this document to link to.

    Usage: {% get_all_doc_versions <docurl> as "varname" %}
    """
    return AllDocVersionsTag.handle(parser, token)


class AllDocVersionsTag(template.Node):
    @classmethod
    def handle(cls, parser, token):
        try:
            tagname, docurl, as_, asvar = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError("Usage: {% get_all_doc_versions <docurl> as <varname> %}")
        return cls(docurl, asvar)

    def __init__(self, docurl, asvar):
        self.docurl = template.Variable(docurl)
        self.asvar = asvar

    def render(self, context):
        try:
            url = self.docurl.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        versions = []
        lang = context.get('lang', 'en')

        # Look for each version of the docs.
        for release in DocumentRelease.objects.filter(lang=lang):
            version_root = get_doc_root(release.lang, release.version)
            if version_root.exists():
                doc_path = get_doc_path(version_root, url)
                if doc_path:
                    versions.append(release.version)

        # Save the versions into the context
        context[self.asvar] = sorted(versions)

        return ''
