import os
from pathlib import Path

from django.test import SimpleTestCase

from ..utils import get_doc_path, sanitize_for_trigram


class TestUtils(SimpleTestCase):
    def test_get_doc_path(self):
        # non-existent file
        self.assertEqual(get_doc_path(Path("root"), "subpath.txt"), None)

        # existing file
        path, filename = __file__.rsplit(os.path.sep, 1)
        self.assertEqual(get_doc_path(Path(path), filename), None)

    def test_sanitize_for_trigram(self):
        for query, sanitized_query in [
            ("simple search", "simple search"),
            ("Python Django -Flask", "Python Django"),
            ('Python "Django Framework" -Flask', "Python Django Framework"),
            ("Développement -'Framework Django' web", "Developpement web"),
            (
                "Γλώσσα προγραμματισμού Python -'Flask και Django'",
                "Γλωσσα προγραμματισμου Python",
            ),
            (
                "Pemrograman Python -'Flask dan Django' backend",
                "Pemrograman Python backend",
            ),
            (
                "Programmazione 'Python e Django' -Flask",
                "Programmazione Python e Django",
            ),
            ("Linguagem Python -'Django e Flask' web", "Linguagem Python web"),
            ("Desarrollo Python -'Django y Flask' rápido", "Desarrollo Python rapido"),
        ]:
            with self.subTest(query=query):
                self.assertEqual(sanitize_for_trigram(query), sanitized_query)
