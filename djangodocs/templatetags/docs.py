from django import template
from django.conf import settings
from unipath import FSPath as Path
from djangodocs.forms import SearchForm

register = template.Library()

@register.inclusion_tag('docs/search_form.html', takes_context=True)
def search_form(context, search_form_id='search'):
    request = context['request']
    auto_id = 'id_%s_%%s' % search_form_id
    return {
        'form': SearchForm(initial=request.GET, auto_id=auto_id),
        'search_form_id': search_form_id,
        'action': context['search'],
    }

@register.tag
def get_all_doc_versions(parser, token):
    """
    Get a list of all versions of this document to link to.
    """
    try:
        tagname, docurl, as_, asvar = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Usage: {% get_all_doc_versions <docurl> as <varname> %}")
    return AllDocVersionsTag(template.Variable(docurl), asvar)
    
class AllDocVersionsTag(template.Node):
    def __init__(self, docurl, asvar):
        self.docurl = docurl
        self.asvar = asvar
        
    def render(self, context):
        try:
            url = self.docurl.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        versions = []
        docroot = Path(settings.DOCS_PICKLE_ROOT).child(settings.DOCS_DEFAULT_LANGUAGE)
    
        # Look for each version of the docs.
        versions_to_check = ['dev', settings.DOCS_DEFAULT_VERSION] + settings.DOCS_PREVIOUS_VERSIONS
        for version in versions_to_check:
            version_root = docroot.child(version, '_build', 'json')
        
            # First try path/to/doc/index.fjson
            bits = url.strip('/').split('/') + ['index.fjson']
            doc = version_root.child(*bits)
            if not doc.exists():
                # Then try path/to/doc.fjson
                bits = bits[:-2] + ['%s.fjson' % bits[-2]]
                doc = version_root.child(*bits)
                if not doc.exists():
                    # Neither exists, so try next.
                    continue
                
            # If we fall through to here, then the doc exists, so note that fact.
            versions.append(version)
        
        # Save the versions into the context
        context[self.asvar] = versions

        return ''