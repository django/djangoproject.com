import os
import re
import subprocess
from collections import OrderedDict

from django.core.files.temp import NamedTemporaryFile
from django.utils.encoding import smart_str

from sorl.thumbnail.base import EXTENSIONS
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.base import EngineBase

size_re = re.compile(r'^(?:.+) (?P<x>\d+)x(?P<y>\d+)')


class Engine(EngineBase):
    """
    Image object is a dict with source path, options and size
    """

    def write(self, image, options, thumbnail):
        """
        Writes the thumbnail image
        """

        args = settings.THUMBNAIL_VIPSTHUMBNAIL.split(' ')
        args.append(image['source'])

        for k in image['options']:
            v = image['options'][k]
            args.append('--%s' % k)
            if v is not None:
                args.append('%s' % v)

        suffix = '.%s' % EXTENSIONS[options['format']]

        write_options = []
        if options['format'] == 'JPEG' and options.get(
                'progressive', settings.THUMBNAIL_PROGRESSIVE):
            write_options.append("interlace")

        if options['quality']:
            if options['format'] == 'JPEG':
                write_options.append("Q=%d" % options['quality'])

        with NamedTemporaryFile(suffix=suffix, mode='rb') as fp:
            # older vipsthumbails used -o, this was renamed to -f in 8.0, use
            # -o here for commpatibility
            args.append("-o")
            args.append(fp.name + "[%s]" % ",".join(write_options))

            args = map(smart_str, args)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            out, err = p.communicate()

            if err:
                raise Exception(err)

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
            args = settings.THUMBNAIL_VIPSHEADER.split(' ')
            args.append(image['source'])
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            m = size_re.match(str(p.stdout.read()))
            image['size'] = int(m.group('x')), int(m.group('y'))
        return image['size']

    def is_valid_image(self, raw_data):
        """
        vipsheader will try a lot of formats, including all those supported by
        imagemagick if compiled with magick support, this can take a while
        """
        with NamedTemporaryFile(mode='wb') as fp:
            fp.write(raw_data)
            fp.flush()
            args = settings.THUMBNAIL_VIPSHEADER.split(' ')
            args.append(fp.name)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            retcode = p.wait()
        return retcode == 0

    def _orientation(self, image):
        # vipsthumbnail also corrects the orientation exif data for
        # destination
        image['options']['rotate'] = None

        return image

    def _colorspace(self, image, colorspace):
        """
        vipsthumbnail does not support greyscaling of images, but pretend it
        does
        """
        return image

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        image['options']['size'] = '%sx%s' % (width, height)
        image['size'] = (width, height)  # update image size
        return image
