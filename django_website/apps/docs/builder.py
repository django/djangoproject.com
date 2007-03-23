"""
Code to do the ReST --> HTML generation for the docs.
"""

import re
import compiler
import smartypants
from docutils import nodes
from docutils.core import publish_parts
from docutils.writers import html4css1

def build_document(text):
    """
    Build a doc file into a dict of HTML bits.
    """
    return publish_parts(text, writer=DjangoHTMLWriter(), settings_overrides={'initial_header_level': 2})

docstring_re = re.compile(r"([\"']{3})(.*?)(\1)", re.DOTALL|re.MULTILINE)
def build_model_document(text):
    """
    Build a test example into a dict of HTML bits.
    """
    # We need to parse the model file without actually executing it.
    tree = compiler.parse(text)
    
    # Get the title and blurb from the module's docstring
    title, blurb = tree.doc.strip().split('\n', 1)
    parts = publish_parts(blurb, writer=DjangoHTMLWriter(), settings_overrides={'initial_header_level': 2})
    parts["title"] = title
    
    # Walk the tree and parse out the bits we care about.
    visitor = compiler.walk(tree, ModelSourceVistor())
    parts["api_usage"] = visitor.doctest
    parts["models"] = visitor.models
    parts["newstyle"] = visitor.newstyle
    
    # Parse out the model source.
    if visitor.newstyle:
        model_source = text[:text.index("__test__")]        
    else:
        model_source = text[:text.index("API_TESTS")]
    parts["model_source"] = model_source.replace(tree.doc, "").replace('""""""\n', '\n').strip()
    
    return parts

class ModelSourceVistor:
    """AST visitor for a model module."""
    
    def __init__(self):
        self.doctest = ""
        self.models = []
        self.newstyle = True
    
    def visitAssign(self, node):
        assname, valtree = node.getChildren()
        if assname.name == "__test__":
            self.doctest = valtree.getChildren()[1].value
        elif assname.name == "API_TESTS":
            self.newstyle = False
            self.doctest = valtree.value
            
    def visitClass(self, node):
        if node.bases and node.bases[0].attrname == "Model":
            self.models.append(node.name)

class DjangoHTMLWriter(html4css1.Writer):
    """
    HTML writer that adds a "toc" key to the set of doc parts.
    """
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
    """
    reST -> HTML translator subclass that fixes up the parts of docutils I don't like.
    """
    
    # Prevent name attributes from being generated
    named_tags = []
    
    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)
        self._in_literal = 0
    
    # Remove the default border=1 from <table>    
    def visit_table(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    # Prevent <h3> from becoming <h3><a id>
    #def visit_title(self, node, move_ids=1):
    #    if isinstance(node.parent, nodes.Admonition):
    #        self.body.append(self.starttag(node, 'p', '', CLASS='admonition-title'))
    #        self.context.append("</p>\n")
    #    else:
    #        html4css1.HTMLTranslator.visit_title(self, node, move_ids=0)
    
    #
    # Apply smartypants to content when not inside literals
    #
    def visit_literal_block(self, node):
        self._in_literal += 1
        html4css1.HTMLTranslator.visit_literal_block(self, node)

    def depart_literal_block(self, node):
        html4css1.HTMLTranslator.depart_literal_block(self, node)
        self._in_literal -= 1
     
    def visit_literal(self, node):
        self._in_literal += 1
        try:
            html4css1.HTMLTranslator.visit_literal(self, node)
        finally:
            self._in_literal -= 1
     
    def encode(self, text):
        text = html4css1.HTMLTranslator.encode(self, text)
        if self._in_literal <= 0:
            text = smartypants.smartyPants(text, "qde")
        return text
    
    #
    # Avoid <blockquote>s around merely indented nodes.
    # Adapted from http://thread.gmane.org/gmane.text.docutils.user/742/focus=804
    #
    
    _suppress_blockquote_child_nodes = (
        nodes.bullet_list, nodes.enumerated_list, nodes.definition_list,
        nodes.literal_block, nodes.doctest_block, nodes.line_block, nodes.table
    )
    def _bq_is_valid(self, node):
        return len(node.children) != 1 or not isinstance(node.children[0], self._suppress_blockquote_child_nodes)
                                        
    def visit_block_quote(self, node):
        if self._bq_is_valid(node):
            html4css1.HTMLTranslator.visit_block_quote(self, node)

    def depart_block_quote(self, node):
        if self._bq_is_valid(node):
            html4css1.HTMLTranslator.depart_block_quote(self, node)
        
    
