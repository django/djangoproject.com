from functools import cached_property

from sphinxcontrib.serializinghtml import JSONHTMLBuilder


class PythonObjectsJSONHTMLBuilder(JSONHTMLBuilder):
    name = "pyjson"

    @cached_property
    def domain_objects(self):
        domain = self.env.get_domain("py")
        return [item for item in domain.get_objects() if item[2] != "module"]

    def get_doc_context(self, docname, body, metatags):
        out_dict = super().get_doc_context(docname, body, metatags)
        python_objects = self.get_python_objects(docname)
        out_dict["python_objects"] = python_objects
        out_dict["python_objects_search"] = " ".join(
            # Keeps the code suffix to improve the search results for terms such as
            # "select" for QuerySet.select_related.
            [key.split(".")[-1] for key in python_objects.keys()]
        )
        return out_dict

    def get_python_objects(self, docname):
        entries = {}
        for name, _, _, obj_docname, _, _ in self.domain_objects:
            if obj_docname == docname:
                code_path = name.split(".")[-2:]
                if code_path[0][0].isupper():
                    short_name = ".".join(code_path)
                else:
                    short_name = code_path[-1]
                entries[short_name] = name
        return entries


def setup(app):
    app.add_builder(PythonObjectsJSONHTMLBuilder)
