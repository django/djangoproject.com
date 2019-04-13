from __future__ import unicode_literals, with_statement
import re
import os
import subprocess
import logging
from collections import OrderedDict

from django.utils.encoding import smart_str
from django.core.files.temp import NamedTemporaryFile

from sorl.thumbnail.base import EXTENSIONS
from sorl.thumbnail.compat import b
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.base import EngineBase

logger = logging.getLogger(__name__)

size_re = re.compile(r'^(?:.+) (?:[A-Z]+) (?P<x>\d+)x(?P<y>\d+)')


class Engine(EngineBase):
    """
    Image object is a dict with source path, options and size
    """

    def write(self, image, options, thumbnail):
        """
        Writes the thumbnail image
        """
        if options['format'] == 'JPEG' and options.get(
                'progressive', settings.THUMBNAIL_PROGRESSIVE):
            image['options']['interlace'] = 'line'

        image['options']['quality'] = options['quality']

        args = settings.THUMBNAIL_CONVERT.split(' ')
        args.append(image['source'] + '[0]')

        for k in image['options']:
            v = image['options'][k]
            args.append('-%s' % k)
            if v is not None:
                args.append('%s' % v)

        flatten = "on"
        if 'flatten' in options:
            flatten = options['flatten']

        if settings.THUMBNAIL_FLATTEN and not flatten == "off":
            args.append('-flatten')

        suffix = '.%s' % EXTENSIONS[options['format']]

        with NamedTemporaryFile(suffix=suffix, mode='rb') as fp:
            args.append(fp.name)
            args = map(smart_str, args)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            returncode = p.wait()
            out, err = p.communicate()

            if returncode:
                raise EngineError(
                    "The command %r exited with a non-zero exit code and printed this to stderr: %s"
                    % (args, err)
                )
            elif err:
                logger.error("Captured stderr: %s", err)

            thumbnail.write(fp.read())

    def cleanup(self, image):
        os.remove(image['source'])  # we should not need this now

    def get_image(self, source):
        """
        Returns the backend image objects from a ImageFile instance
        """
        with NamedTemporaryFile(mode='wb', delete=False) as fp:
            fp.write(source.read())
        return {'source': fp.name, 'options': OrderedDict(), 'size': None}

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        if image['size'] is None:
            args = settings.THUMBNAIL_IDENTIFY.split(' ')
            args.append(image['source'] + '[0]')
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            m = size_re.match(str(p.stdout.read()))
            image['size'] = int(m.group('x')), int(m.group('y'))
        return image['size']

    def is_valid_image(self, raw_data):
        """
        This is not very good for imagemagick because it will say anything is
        valid that it can use as input.
        """
        with NamedTemporaryFile(mode='wb') as fp:
            fp.write(raw_data)
            fp.flush()
            args = settings.THUMBNAIL_IDENTIFY.split(' ')
            args.append(fp.name + '[0]')
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            retcode = p.wait()
        return retcode == 0

    def _orientation(self, image):
        # return image
        # XXX need to get the dimensions right after a transpose.

        if settings.THUMBNAIL_CONVERT.endswith('gm convert'):
            args = settings.THUMBNAIL_IDENTIFY.split()
            args.extend(['-format', '%[exif:orientation]', image['source'] + '[0]'])
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            result = p.stdout.read().strip()
            if result and result != b('unknown'):
                result = int(result)
                options = image['options']
                if result == 2:
                    options['flop'] = None
                elif result == 3:
                    options['rotate'] = '180'
                elif result == 4:
                    options['flip'] = None
                elif result == 5:
                    options['rotate'] = '90'
                    options['flop'] = None
                elif result == 6:
                    options['rotate'] = '90'
                elif result == 7:
                    options['rotate'] = '-90'
                    options['flop'] = None
                elif result == 8:
                    options['rotate'] = '-90'
        else:
            # ImageMagick also corrects the orientation exif data for
            # destination
            image['options']['auto-orient'] = None
        return image

    def _flip_dimensions(self, image):
        if settings.THUMBNAIL_CONVERT.endswith('gm convert'):
            args = settings.THUMBNAIL_IDENTIFY.split()
            args.extend(['-format', '%[exif:orientation]', image['source'] + '[0]'])
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            result = p.stdout.read().strip()
            return result and result != 'unknown' and int(result) in [5, 6, 7, 8]
        else:
            return False

    def _colorspace(self, image, colorspace):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        image['options']['colorspace'] = colorspace
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        """
        Crops the image
        """
        image['options']['crop'] = '%sx%s+%s+%s' % (width, height, x_offset, y_offset)
        image['size'] = (width, height)  # update image size
        return image

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        image['options']['scale'] = '%sx%s!' % (width, height)
        image['size'] = (width, height)  # update image size
        return image

    def _padding(self, image, geometry, options):
        """
        Pads the image
        """
        # The order is important. The gravity option should come before extent.
        image['options']['background'] = options.get('padding_color')
        image['options']['gravity'] = 'center'
        image['options']['extent'] = '%sx%s' % (geometry[0], geometry[1])
        return image


class EngineError(Exception):
    pass
