"""
Script to build the documentation for Django from ReST -> HTML.

Builds each text file in sys.argv (or settings.DJANGO_DOCUMENT_ROOT_PATH) into
two files: a ".html" file with the document contents and a "_toc.html" file
with the TOC.
"""

from django.conf import settings
from django.core import meta, template
from docutils import nodes, utils
from docutils.core import publish_parts
from docutils.writers import html4css1
import glob, inspect, os, re, sys

SETTINGS = {
    'initial_header_level': 2
}

MODEL_DOC_TEMPLATE = """
<div class="document" id="model-{{ model_name }}">

<h1 class="title">{{ title }}</h1>
{{ blurb }}

<h2 id="model-source-code">Model source code</h2>
<pre class="literal-block">{{ model_source }}</pre>

<h2 id="api-reference">API reference</h2>

{% for model in models %}
<h3>{{ model.name }} objects have the following methods:</h3>
<ul>
{% for method in model.methods %}<li><tt class="docutils literal"><span class="pre">{{ method }}()</span></tt></li>
{% endfor %}</ul>
{% endfor %}

<h2 id="sample-usage">Sample API usage</h2>
<p>This sample code assumes the above model{{ models|pluralize }} {% if models|pluralize %}have{% else %}has{% endif %}
been saved in a file <tt class="docutils literal"><span class="pre">examplemodel.py</span></tt>.
<pre class="literal-block">&gt;&gt;&gt; from django.models.examplemodel import {% for model in models %}{{ model.module_name }}{% if not forloop.last %}, {% endif %}{% endfor %}
{{ api_usage }}</pre>
</div>
"""

MODEL_TOC = """
<ul>
<li><a href="#model-source-code">Model source code</a></li>
<li><a href="#api-reference">API reference</a></li>
<li><a href="#sample-usage">Sample API usage</a></li>
</ul>
"""

def build_documents():
    writer = DjangoHTMLWriter()
    for fname in glob.glob1(settings.DJANGO_DOCUMENT_ROOT_PATH, "*.txt"):
        in_file = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, fname)
        out_file = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, os.path.splitext(fname)[0] + ".html")
        toc_file = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, os.path.splitext(fname)[0] + "_toc.html")
        parts = publish_parts(
            open(in_file).read(),
            source_path=in_file,
            destination_path=out_file,
            writer=writer,
            settings_overrides=SETTINGS,
        )
        open(out_file, 'w').write(parts['html_body'])
        open(toc_file, 'w').write(parts['toc'])

def build_test_documents():
    sys.path.insert(0, settings.DJANGO_TESTS_PATH)
    writer = DjangoHTMLWriter()
    import runtests

    # Manually set INSTALLED_APPS to point to the test app.
    settings.INSTALLED_APPS = (runtests.APP_NAME,)

    # Some of the test models need to know whether the docs are being built.
    settings.BUILDING_DOCS = True

    for model_name in runtests.get_test_models():
        mod = meta.get_app(model_name)

        out_file = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, 'model_' + model_name + '.html')
        toc_file = os.path.join(settings.DJANGO_DOCUMENT_ROOT_PATH, 'model_' + model_name + '_toc.html')

        # Clean up the title and blurb.
        title, blurb = mod.__doc__.strip().split('\n', 1)
        parts = publish_parts(
            blurb,
            source_path=mod.__file__,
            destination_path=out_file,
            writer=writer,
            settings_overrides=SETTINGS,
        )
        blurb = parts["html_body"]
        api_usage = mod.API_TESTS

        # Get the source code of the model, without the docstring or the
        # API_TESTS variable.
        model_source = inspect.getsource(mod)
        model_source = model_source.replace(mod.__doc__, '')
        model_source = model_source.replace(mod.API_TESTS, '')
        model_source = model_source.replace('""""""\n', '\n')
        model_source = re.sub(r'(?s)API_TESTS = .*', '', model_source)
        model_source = model_source.strip()

        models = []
        for m in mod._MODELS:
            models.append({
                'name': m._meta.object_name,
                'module_name': m._meta.module_name,
                'methods': [method for method in dir(m) if not method.startswith('_')],
            })

        # Run this through the template system.
        t = template.Template(MODEL_DOC_TEMPLATE)
        c = template.Context(locals())
        html = t.render(c)

        try:
            fp = open(out_file, 'w')
        except IOError:
            sys.stderr.write("Couldn't write to %s.\n" % file_name)
            continue
        else:
            fp.write(html)
            fp.close()

        try:
            fp = open(toc_file, 'w')
        except IOError:
            sys.stderr.write("Couldn't write to %s.\n" % file_name)
            continue
        else:
            fp.write(MODEL_TOC)
            fp.close()

class DjangoHTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = DjangoHTMLTranslator

    def translate(self):
        # build the document
        html4css1.Writer.translate(self)

        # build the contents
        contents = self.build_contents(self.document)
        contents_doc = self.document.copy()
        contents_doc.children = contents
        contents_visitor = self.translator_class(contents_doc)
        contents_doc.walkabout(contents_visitor)
        self.parts['toc'] = "<ul class='toc'>%s</ul>" % ''.join(contents_visitor.fragment)

    def build_contents(self, node, level=0):
        level += 1
        sections = []
        i = len(node) - 1
        while i >= 0 and isinstance(node[i], nodes.section):
            sections.append(node[i])
            i -= 1
        sections.reverse()
        entries = []
        autonum = 0
        depth = 4   # XXX FIXME
        for section in sections:
            title = section[0]
            entrytext = title
            try:
                reference = nodes.reference('', '', refid=section['ids'][0], *entrytext)
            except IndexError:
                continue
            ref_id = self.document.set_id(reference)
            entry = nodes.paragraph('', '', reference)
            item = nodes.list_item('', entry)
            if level < depth:
                subsects = self.build_contents(section, level)
                item += subsects
            entries.append(item)
        if entries:
            contents = nodes.bullet_list('', *entries)
            return contents
        else:
            return []

class DjangoHTMLTranslator(html4css1.HTMLTranslator):
    def visit_table(self, node):
        """Remove the damn border=1 from the standard HTML writer"""
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    def visit_title(self, node):
        """Coppied from html4css1.Writer wholesale just to get rid of the <a name=> crap.  Fun, eh?"""
        check_id = 0
        close_tag = '</p>\n'
        if isinstance(node.parent, nodes.topic):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='topic-title first'))
            check_id = 1
        elif isinstance(node.parent, nodes.sidebar):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='sidebar-title'))
            check_id = 1
        elif isinstance(node.parent, nodes.Admonition):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='admonition-title'))
            check_id = 1
        elif isinstance(node.parent, nodes.table):
            self.body.append(
                  self.starttag(node, 'caption', ''))
            check_id = 1
            close_tag = '</caption>\n'
        elif isinstance(node.parent, nodes.document):
            self.body.append(self.starttag(node, 'h1', '', CLASS='title'))
            self.context.append('</h1>\n')
            self.in_document_title = len(self.body)
        else:
            assert isinstance(node.parent, nodes.section)
            h_level = self.section_level + self.initial_header_level - 1
            atts = {}
            if (len(node.parent) >= 2 and
                isinstance(node.parent[1], nodes.subtitle)):
                atts['CLASS'] = 'with-subtitle'
            node.ids = node.parent['ids']
            self.body.append(self.starttag(node, 'h%s' % h_level, '', **atts))
            self.context.append('</h%s>\n' % (h_level))
        if check_id:
            if node.parent['ids']:
                self.body.append(
                    self.starttag({}, 'a', '', name=node.parent['ids'][0]))
                self.context.append('</a>' + close_tag)
            else:
                self.context.append(close_tag)


if __name__ == "__main__":
    build_documents()
    build_test_documents()