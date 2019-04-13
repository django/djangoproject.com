# encoding=utf-8

from __future__ import unicode_literals, division
import json
import os
import re

from django.core.files.base import File, ContentFile
from django.core.files.storage import Storage  # , default_storage
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import LazyObject, empty
from sorl.thumbnail import default
from sorl.thumbnail.conf import settings
from sorl.thumbnail.compat import (urlopen, urlparse, urlsplit,
                                   quote, quote_plus, URLError, encode)
from sorl.thumbnail.default import storage as default_storage
from sorl.thumbnail.helpers import ThumbnailError, tokey, get_module_class, deserialize
from sorl.thumbnail.parsers import parse_geometry

url_pat = re.compile(r'^(https?|ftp):\/\/')


def serialize_image_file(image_file):
    if image_file.size is None:
        raise ThumbnailError('Trying to serialize an ``ImageFile`` with a '
                             '``None`` size.')
    data = {
        'name': image_file.name,
        'storage': image_file.serialize_storage(),
        'size': image_file.size,
    }
    return json.dumps(data)


def deserialize_image_file(s):
    data = deserialize(s)

    class LazyStorage(LazyObject):
        def _setup(self):
            self._wrapped = get_module_class(data['storage'])()

    image_file = ImageFile(data['name'], LazyStorage())
    image_file.set_size(data['size'])
    return image_file


class BaseImageFile(object):
    size = []

    def exists(self):
        raise NotImplementedError()

    @property
    def width(self):
        return self.size[0]

    x = width

    @property
    def height(self):
        return self.size[1]

    y = height

    def is_portrait(self):
        return self.y > self.x

    @property
    def ratio(self):
        return float(self.x) / float(self.y)

    @property
    def url(self):
        raise NotImplementedError()

    src = url


@python_2_unicode_compatible
class ImageFile(BaseImageFile):
    _size = None

    def __init__(self, file_, storage=None):
        if not file_:
            raise ThumbnailError('File is empty.')

        # figure out name
        if hasattr(file_, 'name'):
            self.name = file_.name
        else:
            self.name = force_text(file_)

        # TODO: Add a customizable naming method as a signal

        # Remove query args from names. Fixes cache and signature arguments
        # from third party services, like Amazon S3 and signature args.
        if settings.THUMBNAIL_REMOVE_URL_ARGS:
            self.name = self.name.split('?')[0]

        # Support for relative protocol urls
        if self.name.startswith('//'):
            self.name = 'http:' + self.name

        # figure out storage
        if storage is not None:
            self.storage = storage
        elif hasattr(file_, 'storage'):
            self.storage = file_.storage
        elif url_pat.match(self.name):
            self.storage = UrlStorage()
        else:
            self.storage = default_storage

        if hasattr(self.storage, 'location'):
            location = self.storage.location
            if not self.storage.location.endswith("/"):
                location += "/"
            if self.name.startswith(location):
                self.name = self.name[len(location):]

    def __str__(self):
        return self.name

    def exists(self):
        return self.storage.exists(self.name)

    def set_size(self, size=None):
        # set the size if given
        if size is not None:
            pass
        # Don't try to set the size the expensive way if it already has a
        # value.
        elif self._size is not None:
            return
        elif hasattr(self.storage, 'image_size'):
            # Storage backends can implement ``image_size`` method that
            # optimizes this.
            size = self.storage.image_size(self.name)
        else:
            # This is the worst case scenario
            image = default.engine.get_image(self)
            size = default.engine.get_image_size(image)
            if self.flip_dimensions(image):
                size = list(size)
                size.reverse()
        self._size = list(size)

    def flip_dimensions(self, image):
        """
        Do not manipulate image, but ask engine whether we'd be doing a 90deg
        rotation at some point.
        """
        return default.engine.flip_dimensions(image)

    @property
    def size(self):
        return self._size

    @property
    def url(self):
        return self.storage.url(self.name)

    def read(self):
        f = self.storage.open(self.name)
        try:
            return f.read()
        finally:
            f.close()

    def write(self, content):
        if not isinstance(content, File):
            content = ContentFile(content)

        self._size = None
        self.name = self.storage.save(self.name, content)

        return self.name

    def delete(self):
        return self.storage.delete(self.name)

    def serialize_storage(self):
        if isinstance(self.storage, LazyObject):
            # if storage is wrapped in a lazy object we need to get the real
            # thing.
            if self.storage._wrapped is empty:
                self.storage._setup()
            cls = self.storage._wrapped.__class__
        else:
            cls = self.storage.__class__
        return '%s.%s' % (cls.__module__, cls.__name__)

    @property
    def key(self):
        return tokey(self.name, self.serialize_storage())

    def serialize(self):
        return serialize_image_file(self)


class DummyImageFile(BaseImageFile):
    def __init__(self, geometry_string):
        self.size = parse_geometry(
            geometry_string,
            settings.THUMBNAIL_DUMMY_RATIO,
        )

    def exists(self):
        return True

    @property
    def url(self):
        return settings.THUMBNAIL_DUMMY_SOURCE % (
            {'width': self.x, 'height': self.y}
        )


class UrlStorage(Storage):
    def normalize_url(self, url, charset='utf-8'):
        url = encode(url, charset, 'ignore')
        scheme, netloc, path, qs, anchor = urlsplit(url)

        path = quote(path, b'/%')
        qs = quote_plus(qs, b':&%=')

        return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

    def open(self, name, mode='rb'):
        return urlopen(self.normalize_url(name))

    def exists(self, name):
        try:
            self.open(name)
        except URLError:
            return False
        return True

    def url(self, name):
        return name

    def delete(self, name):
        pass


def delete_all_thumbnails():
    storage = default.storage
    path = settings.THUMBNAIL_PREFIX

    def walk(path):
        dirs, files = storage.listdir(path)
        for f in files:
            storage.delete(os.path.join(path, f))
        for d in dirs:
            directory = os.path.join(path, d)
            walk(directory)
            try:
                full_path = storage.path(directory)
            except Exception:
                continue
            os.rmdir(full_path)

    walk(path)
