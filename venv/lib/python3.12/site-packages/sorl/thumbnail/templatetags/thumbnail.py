import decimal
import logging
import os
import re
import sys
from functools import wraps

from django.conf import settings
from django.template import Library, Node, NodeList, TemplateSyntaxError
from django.utils.encoding import smart_str

from sorl.thumbnail import default
from sorl.thumbnail.conf import settings as sorl_settings
from sorl.thumbnail.images import DummyImageFile, ImageFile
from sorl.thumbnail.parsers import parse_geometry
from sorl.thumbnail.shortcuts import get_thumbnail

register = Library()
kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')
logger = logging.getLogger('sorl.thumbnail')


def safe_filter(error_output=''):
    """
    A safe filter decorator only raising errors when ``THUMBNAIL_DEBUG`` is
    ``True`` otherwise returning ``error_output``.
    """

    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as err:
                if sorl_settings.THUMBNAIL_DEBUG:
                    raise
                logger.error('Thumbnail filter failed: %s' % str(err),
                             exc_info=sys.exc_info())
                return error_output

        return wrapper

    return inner


class ThumbnailNodeBase(Node):
    """
    A Node that renders safely
    """
    nodelist_empty = NodeList()

    def render(self, context):

        try:
            return self._render(context)
        except Exception:
            if sorl_settings.THUMBNAIL_DEBUG:
                raise

            error_message = 'Thumbnail tag failed'

            if context.template.engine.debug:
                try:
                    error_message_template = (
                        "Thumbnail tag failed "
                        "in template {template_name}, error at: "
                        "{tag_text}"
                    )
                    template_origin, (position_start, position_end) = self.source
                    template_text = template_origin.reload()
                    tag_text = template_text[position_start:position_end]

                    error_message = error_message_template.format(
                        template_name=template_origin.name,
                        tag_text=tag_text,
                    )
                except Exception:
                    pass

            logger.exception(error_message)

            return self.nodelist_empty.render(context)

    def _render(self, context):
        raise NotImplementedError()


class ThumbnailNode(ThumbnailNodeBase):
    child_nodelists = ('nodelist_file', 'nodelist_empty')
    error_msg = ('Syntax error. Expected: ``thumbnail source geometry '
                 '[key1=val1 key2=val2...] as var``')

    def __init__(self, parser, token):
        bits = token.split_contents()
        self.file_ = parser.compile_filter(bits[1])
        self.geometry = parser.compile_filter(bits[2])
        self.options = []
        self.as_var = None
        self.nodelist_file = None

        if bits[-2] == 'as':
            options_bits = bits[3:-2]
        else:
            options_bits = bits[3:]

        for bit in options_bits:
            m = kw_pat.match(bit)
            if not m:
                raise TemplateSyntaxError(self.error_msg)
            key = smart_str(m.group('key'))
            expr = parser.compile_filter(m.group('value'))
            self.options.append((key, expr))

        if bits[-2] == 'as':
            self.as_var = bits[-1]
            self.nodelist_file = parser.parse(('empty', 'endthumbnail',))
            if parser.next_token().contents == 'empty':
                self.nodelist_empty = parser.parse(('endthumbnail',))
                parser.delete_first_token()

    def _render(self, context):
        file_ = self.file_.resolve(context)
        geometry = self.geometry.resolve(context)
        options = {}
        for key, expr in self.options:
            noresolve = {'True': True, 'False': False, 'None': None}
            value = noresolve.get(str(expr), expr.resolve(context))
            if key == 'options':
                options.update(value)
            else:
                options[key] = value

        thumbnail = None
        if file_:
            thumbnail = get_thumbnail(file_, geometry, **options)
        elif sorl_settings.THUMBNAIL_DUMMY:
            thumbnail = DummyImageFile(geometry)

        if not thumbnail or (isinstance(thumbnail, DummyImageFile) and self.nodelist_empty):
            if self.nodelist_empty:
                return self.nodelist_empty.render(context)
            else:
                return ''

        if self.as_var:
            context.push()
            context[self.as_var] = thumbnail
            output = self.nodelist_file.render(context)
            context.pop()
        else:
            output = thumbnail.url

        return output

    def __repr__(self):
        return "<ThumbnailNode>"

    def __iter__(self):
        for node in self.nodelist_file:
            yield node
        for node in self.nodelist_empty:
            yield node


@register.filter
def resolution(file_, resolution_string):
    """
    A filter to return the URL for the provided resolution of the thumbnail.
    """
    if sorl_settings.THUMBNAIL_DUMMY:
        dummy_source = sorl_settings.THUMBNAIL_DUMMY_SOURCE
        source = dummy_source.replace('%(width)s', '(?P<width>[0-9]+)')
        source = source.replace('%(height)s', '(?P<height>[0-9]+)')
        source = re.compile(source)
        try:
            resolution = decimal.Decimal(resolution_string.strip('x'))
            info = source.match(file_).groupdict()
            info = {dimension: int(int(size) * resolution) for (dimension, size) in info.items()}
            return dummy_source % info
        except (AttributeError, TypeError, KeyError):
            # If we can't manipulate the dummy we shouldn't change it at all
            return file_

    filename, extension = os.path.splitext(file_)
    return '%s@%s%s' % (filename, resolution_string, extension)


@register.tag
def thumbnail(parser, token):
    return ThumbnailNode(parser, token)


@register.filter
@safe_filter(error_output=False)
def is_portrait(file_):
    """
    A very handy filter to determine if an image is portrait or landscape.
    """
    if sorl_settings.THUMBNAIL_DUMMY:
        return sorl_settings.THUMBNAIL_DUMMY_RATIO < 1
    if not file_:
        return False
    image_file = default.kvstore.get_or_set(ImageFile(file_))
    return image_file.is_portrait()


@register.filter
@safe_filter(error_output='auto')
def margin(file_, geometry_string):
    """
    Returns the calculated margin for an image and geometry
    """

    if not file_ or (sorl_settings.THUMBNAIL_DUMMY or isinstance(file_, DummyImageFile)):
        return 'auto'

    margin = [0, 0, 0, 0]

    image_file = default.kvstore.get_or_set(ImageFile(file_))

    x, y = parse_geometry(geometry_string, image_file.ratio)
    ex = x - image_file.x
    margin[3] = ex / 2
    margin[1] = ex / 2

    if ex % 2:
        margin[1] += 1

    ey = y - image_file.y
    margin[0] = ey / 2
    margin[2] = ey / 2

    if ey % 2:
        margin[2] += 1

    return ' '.join(['%dpx' % n for n in margin])


@register.filter
@safe_filter(error_output='auto')
def background_margin(file_, geometry_string):
    """
    Returns the calculated margin for a background image and geometry
    """
    if not file_ or sorl_settings.THUMBNAIL_DUMMY:
        return 'auto'

    margin = [0, 0]
    image_file = default.kvstore.get_or_set(ImageFile(file_))
    x, y = parse_geometry(geometry_string, image_file.ratio)
    ex = x - image_file.x
    margin[0] = ex / 2
    ey = y - image_file.y
    margin[1] = ey / 2

    return ' '.join(['%spx' % n for n in margin])


def text_filter(regex_base, value):
    """
    Helper method to regex replace images with captions in different markups
    """
    regex = regex_base % {
        're_cap': r'[a-zA-Z0-9\.\,:;/_ \(\)\-\!\?"]+',
        're_img': r'[a-zA-Z0-9\.:/_\-\% ]+'
    }
    images = re.findall(regex, value)

    for i in images:
        image = i[1]
        if image.startswith(settings.MEDIA_URL):
            image = image[len(settings.MEDIA_URL):]

        im = get_thumbnail(image, str(sorl_settings.THUMBNAIL_FILTER_WIDTH))
        value = value.replace(i[1], im.url)

    return value


@register.filter
@safe_filter(error_output='auto')
def markdown_thumbnails(value):
    return text_filter(r'!\[(%(re_cap)s)?\][ ]?\((%(re_img)s)\)', value)


@register.filter
@safe_filter(error_output='auto')
def html_thumbnails(value):
    return text_filter(r'<img(?: alt="(%(re_cap)s)?")? src="(%(re_img)s)"', value)
