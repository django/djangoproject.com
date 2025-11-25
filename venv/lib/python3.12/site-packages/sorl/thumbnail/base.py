import logging
import os
import re

from sorl.thumbnail import default
from sorl.thumbnail.conf import defaults as default_settings
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import serialize, tokey
from sorl.thumbnail.images import DummyImageFile, ImageFile
from sorl.thumbnail.parsers import parse_geometry

logger = logging.getLogger(__name__)

EXTENSIONS = {
    'JPEG': 'jpg',
    'PNG': 'png',
    'GIF': 'gif',
    'WEBP': 'webp',
}


class ThumbnailBackend:
    """
    The main class for sorl-thumbnail, you can subclass this if you for example
    want to change the way destination filename is generated.
    """

    default_options = {
        'format': settings.THUMBNAIL_FORMAT,
        'quality': settings.THUMBNAIL_QUALITY,
        'colorspace': settings.THUMBNAIL_COLORSPACE,
        'upscale': settings.THUMBNAIL_UPSCALE,
        'crop': False,
        'cropbox': None,
        'rounded': None,
        'padding': settings.THUMBNAIL_PADDING,
        'padding_color': settings.THUMBNAIL_PADDING_COLOR,
    }

    extra_options = (
        ('progressive', 'THUMBNAIL_PROGRESSIVE'),
        ('orientation', 'THUMBNAIL_ORIENTATION'),
        ('blur', 'THUMBNAIL_BLUR'),
    )

    def file_extension(self, source):
        return os.path.splitext(source.name)[1].lower()

    def _get_format(self, source):
        file_extension = self.file_extension(source)

        if file_extension == '.jpg' or file_extension == '.jpeg':
            return 'JPEG'
        elif file_extension == '.png':
            return 'PNG'
        elif file_extension == '.gif':
            return 'GIF'
        elif file_extension == '.webp':
            return 'WEBP'
        else:
            from django.conf import settings

            return getattr(settings, 'THUMBNAIL_FORMAT', default_settings.THUMBNAIL_FORMAT)

    def get_thumbnail(self, file_, geometry_string, **options):
        """
        Returns thumbnail as an ImageFile instance for file with geometry and
        options given. First it will try to get it from the key value store,
        secondly it will create it.
        """
        logger.debug('Getting thumbnail for file [%s] at [%s]', file_, geometry_string)

        if file_:
            source = ImageFile(file_)
        else:
            raise ValueError('falsey file_ argument in get_thumbnail()')

        # preserve image filetype
        if settings.THUMBNAIL_PRESERVE_FORMAT:
            options.setdefault('format', self._get_format(source))

        for key, value in self.default_options.items():
            options.setdefault(key, value)

        # For the future I think it is better to add options only if they
        # differ from the default settings as below. This will ensure the same
        # filenames being generated for new options at default.
        for key, attr in self.extra_options:
            value = getattr(settings, attr)
            if value != getattr(default_settings, attr):
                options.setdefault(key, value)

        name = self._get_thumbnail_filename(source, geometry_string, options)
        thumbnail = ImageFile(name, default.storage)
        cached = default.kvstore.get(thumbnail)

        if cached:
            return cached

        # We have to check exists() because the Storage backend does not
        # overwrite in some implementations.
        if settings.THUMBNAIL_FORCE_OVERWRITE or not thumbnail.exists():
            try:
                source_image = default.engine.get_image(source)
            except Exception as e:
                logger.exception(e)
                if settings.THUMBNAIL_DUMMY:
                    return DummyImageFile(geometry_string)
                else:
                    # if storage backend says file doesn't exist remotely,
                    # don't try to create it and exit early.
                    # Will return working empty image type; 404'd image
                    logger.warning(
                        'Remote file [%s] at [%s] does not exist',
                        file_, geometry_string,
                    )
                    return thumbnail

            # We might as well set the size since we have the image in memory
            image_info = default.engine.get_image_info(source_image)
            options['image_info'] = image_info
            size = default.engine.get_image_size(source_image)
            source.set_size(size)

            try:
                self._create_thumbnail(source_image, geometry_string, options,
                                       thumbnail)
                self._create_alternative_resolutions(source_image, geometry_string,
                                                     options, thumbnail.name)
            finally:
                default.engine.cleanup(source_image)

        # If the thumbnail exists we don't create it, the other option is
        # to delete and write but this could lead to race conditions so I
        # will just leave that out for now.
        default.kvstore.get_or_set(source)
        default.kvstore.set(thumbnail, source)
        return thumbnail

    def delete(self, file_, delete_file=True):
        """
        Deletes file_ references in Key Value store and optionally the file_
        it self.
        """
        image_file = ImageFile(file_)
        if delete_file:
            image_file.delete()
        default.kvstore.delete(image_file)

    def _create_thumbnail(self, source_image, geometry_string, options,
                          thumbnail):
        """
        Creates the thumbnail by using default.engine
        """
        logger.debug('Creating thumbnail file [%s] at [%s] with [%s]',
                     thumbnail.name, geometry_string, options)
        ratio = default.engine.get_image_ratio(source_image, options)
        geometry = parse_geometry(geometry_string, ratio)
        image = default.engine.create(source_image, geometry, options)
        default.engine.write(image, options, thumbnail)
        # It's much cheaper to set the size here
        size = default.engine.get_image_size(image)
        thumbnail.set_size(size)

    def _create_alternative_resolutions(self, source_image, geometry_string,
                                        options, name):
        """
        Creates the thumbnail by using default.engine with multiple output
        sizes.  Appends @<ratio>x to the file name.
        """
        ratio = default.engine.get_image_ratio(source_image, options)
        geometry = parse_geometry(geometry_string, ratio)
        file_name, dot_file_ext = os.path.splitext(name)

        for resolution in settings.THUMBNAIL_ALTERNATIVE_RESOLUTIONS:
            resolution_geometry = (int(geometry[0] * resolution), int(geometry[1] * resolution))
            resolution_options = options.copy()
            if 'crop' in options and isinstance(options['crop'], str):
                crop = options['crop'].split(" ")
                for i in range(len(crop)):
                    s = re.match(r"(\d+)px", crop[i])
                    if s:
                        crop[i] = "%spx" % int(int(s.group(1)) * resolution)
                resolution_options['crop'] = " ".join(crop)

            image = default.engine.create(source_image, resolution_geometry, options)
            thumbnail_name = '%(file_name)s%(suffix)s%(file_ext)s' % {
                'file_name': file_name,
                'suffix': '@%sx' % resolution,
                'file_ext': dot_file_ext
            }
            thumbnail = ImageFile(thumbnail_name, default.storage)
            default.engine.write(image, resolution_options, thumbnail)
            size = default.engine.get_image_size(image)
            thumbnail.set_size(size)

    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        return '%s%s.%s' % (settings.THUMBNAIL_PREFIX, path, EXTENSIONS[options['format']])
