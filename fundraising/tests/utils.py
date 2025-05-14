import shutil
import tempfile
from io import BytesIO

from django.core.files.images import ImageFile
from PIL import Image


def ImageFileFactory(name, width=1, height=1, color=(12, 75, 51)):
    """
    Return an ImageFile instance with the given name.
    The image will be of the given size, and of solid color. The format will
    be inferred from the filename.
    """
    img = Image.new("RGB", (width, height), color=color)
    out = BytesIO()
    img.save(out, format=name.split(".")[-1])
    return ImageFile(out, name=name)


class TemporaryMediaRootMixin:
    """
    A TestCase mixin that overrides settings.MEDIA_ROOT for every test on the
    class to point to a temporary directory that is destroyed when the tests
    finished.
    The content of the directory persists between different tests on the class.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmpdir = tempfile.mkdtemp(prefix="djangoprojectcom_")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)
        super().tearDownClass()

    def run(self, result=None):
        with self.settings(MEDIA_ROOT=self.tmpdir):
            return super().run(result)
