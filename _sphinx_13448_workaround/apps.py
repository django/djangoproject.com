from django.apps import AppConfig
from sphinx.locale import _TranslationProxy
from sphinxcontrib.serializinghtml import jsonimpl


class FixedSphinxJSONEncoder(jsonimpl.SphinxJSONEncoder):
    def default(self, obj):
        if isinstance(obj, _TranslationProxy):
            return str(obj)
        return super().default(obj)


class SphinxBugWorkaroundConfig(AppConfig):
    """
    Add a workaround for sphinx bug https://github.com/sphinx-doc/sphinx/issues/13448
    """

    name = "_sphinx_13448_workaround"
    verbose_name = "Sphinx Bug 13448 Workaround"

    def ready(self):
        from sphinx.domains import python  # noqa: F401

        jsonimpl.SphinxJSONEncoder = FixedSphinxJSONEncoder
