from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from sphinx.testing.util import _clean_up_global_state

from ..builder import DomainObject, PythonObjectsJSONHTMLBuilder


class TestPythonObjectsJSONHTMLBuilder(SimpleTestCase):
    def setUp(self):
        self.app = Mock()
        self.env = Mock()
        self.app.doctreedir = "/tmp"
        self.env.get_domain = Mock()
        self.mock_domain = Mock()
        self.env.get_domain.return_value = self.mock_domain
        self.builder = PythonObjectsJSONHTMLBuilder(self.app, self.env)

    def test_domain_objects_excludes_modules(self):
        self.mock_domain.get_objects.return_value = [
            ("module1", "module1", "module", "doc1", "", 0),
            ("ClassA", "ClassA", "class", "doc2", "", 0),
            ("function_b", "function_b", "function", "doc2", "", 0),
        ]

        expected_objects = [
            DomainObject("ClassA", "ClassA", "class", "doc2", "", 0),
            DomainObject("function_b", "function_b", "function", "doc2", "", 0),
        ]
        self.assertEqual(self.builder.domain_objects, expected_objects)

    def test_get_python_objects(self):
        self.mock_domain.get_objects.return_value = [
            (
                "module1.ClassA.method",
                "module1.ClassA.method",
                "method",
                "doc1",
                "",
                "",
            ),
            ("module1.ClassA", "module1.ClassA", "class", "doc1", "", ""),
            ("module1.function_b", "module1.function_b", "function", "doc1", "", ""),
        ]
        expected_result = {
            "ClassA": "module1.ClassA",
            "ClassA.method": "module1.ClassA.method",
            "function_b": "module1.function_b",
        }
        self.assertEqual(self.builder.get_python_objects("doc1"), expected_result)

    @patch("docs.builder.JSONHTMLBuilder.get_doc_context")
    def test_get_doc_context(self, mock_super_get_doc_context):
        mock_super_get_doc_context.return_value = {}
        self.mock_domain.get_objects.return_value = [
            ("module1", "module1", "module", "doc1", "", ""),
            ("module1.ClassA", "module1.ClassA", "class", "doc1", "", ""),
            ("function_b", "function_b", "function", "doc2", "", ""),
        ]
        result = self.builder.get_doc_context("doc1", "", "")
        self.assertIn("python_objects", result)
        self.assertIn("python_objects_search", result)
        self.assertEqual(result["python_objects"], {"ClassA": "module1.ClassA"})
        self.assertEqual(result["python_objects_search"], "ClassA")


class TestSphinxAPI(SimpleTestCase):
    def test_private_sphinx_function_exists(self):
        _clean_up_global_state()
