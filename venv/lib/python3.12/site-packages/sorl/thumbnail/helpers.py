import hashlib
import json
import math
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_str


class ThumbnailError(Exception):
    pass


class SortedJSONEncoder(json.JSONEncoder):
    """
    A json encoder that sorts the dict keys
    """

    def __init__(self, **kwargs):
        kwargs['sort_keys'] = True
        super().__init__(**kwargs)


def toint(number):
    """
    Helper to return rounded int for a float or just the int it self.
    """
    if isinstance(number, float):
        if number > 1:
            number = round(number, 0)
        else:
            # The following solves when image has small dimensions (like 1x54)
            # then scale factor 1 * 0.296296 and `number` will store `0`
            # that will later raise ZeroDivisionError.
            number = round(math.ceil(number), 0)
    return int(number)


def tokey(*args):
    """
    Computes a unique key from arguments given.
    """
    salt = '||'.join([force_str(arg) for arg in args])
    return hashlib.md5(salt.encode()).hexdigest()


def serialize(obj):
    return json.dumps(obj, cls=SortedJSONEncoder)


def deserialize(s):
    if isinstance(s, bytes):
        return json.loads(s.decode('utf-8'))
    return json.loads(s)


def get_module_class(class_path):
    """
    imports and returns module class from ``path.to.module.Class``
    argument
    """
    mod_name, cls_name = class_path.rsplit('.', 1)

    try:
        mod = import_module(mod_name)
    except ImportError as e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' % (mod_name, e)))

    return getattr(mod, cls_name)
