from dataclasses import dataclass
from functools import cached_property

from sphinxcontrib.serializinghtml import JSONHTMLBuilder

IGNORED_DOMAIN_TYPES = {"module"}


@dataclass
class DomainObject:
    """
    A wrapper around sphinx's domain object descriptions
    https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.Domain.get_objects
    """

    name: str
    dispname: str
    type: str
    docname: str
    anchor: str
    priority: int

    @property
    def short_name(self) -> str:
        """
        Returns a shortened version of the object's name.

        - If the second-to-last part of the name starts with an uppercase letter
          (indicating a class method or class attribute), returns the last two parts.
        - Otherwise, returns only the last part (likely a function, or class).

        Examples:
        - "django.db.models.query.QuerySet.select_related" → "QuerySet.select_related"
        - "django.db.models.query.QuerySet" → "QuerySet"
        - "django.template.context_processors.static" → "static"
        """
        parts = self.name.split(".")

        if len(parts) < 2:
            return self.name

        last, second_last = parts[-1], parts[-2]
        return f"{second_last}.{last}" if second_last[0].isupper() else last


class PythonObjectsJSONHTMLBuilder(JSONHTMLBuilder):
    @cached_property
    def domain_objects(self):
        domain = self.env.get_domain("py")
        return [
            DomainObject(*item)
            for item in domain.get_objects()
            if item[2] not in IGNORED_DOMAIN_TYPES  # item[2] is 'type'.
        ]

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
        return {
            obj.short_name: obj.name
            for obj in self.domain_objects
            if obj.docname == docname
        }


def setup(app):
    app.add_builder(PythonObjectsJSONHTMLBuilder, override=True)

    # JSONHTMLBuilder marks parallel read/write as safe, so our implementation
    # should also handle that.
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
