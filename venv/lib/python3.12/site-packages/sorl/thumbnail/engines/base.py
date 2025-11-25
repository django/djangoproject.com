from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import toint
from sorl.thumbnail.parsers import parse_crop, parse_cropbox


class EngineBase:
    """
    ABC for Thumbnail engines, methods are static
    """

    def create(self, image, geometry, options):
        """
        Processing conductor, returns the thumbnail as an image engine instance
        """
        image = self.cropbox(image, geometry, options)
        image = self.orientation(image, geometry, options)
        image = self.colorspace(image, geometry, options)
        image = self.remove_border(image, options)
        image = self.scale(image, geometry, options)
        image = self.crop(image, geometry, options)
        image = self.rounded(image, geometry, options)
        image = self.blur(image, geometry, options)
        image = self.padding(image, geometry, options)
        return image

    def cropbox(self, image, geometry, options):
        """
        Wrapper for ``_cropbox``
        """
        cropbox = options['cropbox']
        if not cropbox:
            return image
        x, y, x2, y2 = parse_cropbox(cropbox)
        return self._cropbox(image, x, y, x2, y2)

    def orientation(self, image, geometry, options):
        """
        Wrapper for ``_orientation``
        """
        if options.get('orientation', settings.THUMBNAIL_ORIENTATION):
            return self._orientation(image)
        self.reoriented = True
        return image

    def flip_dimensions(self, image, geometry=None, options=None):
        options = options or {}
        reoriented = hasattr(self, 'reoriented')
        if options.get('orientation', settings.THUMBNAIL_ORIENTATION) and not reoriented:
            return self._flip_dimensions(image)
        return False

    def colorspace(self, image, geometry, options):
        """
        Wrapper for ``_colorspace``
        """
        colorspace = options['colorspace']
        return self._colorspace(image, colorspace)

    def remove_border(self, image, options):

        if options.get('remove_border', False):
            x_image, y_image = self.get_image_size(image)
            image = self._remove_border(image, x_image, y_image)

        return image

    def _calculate_scaling_factor(self, x_image, y_image, geometry, options):
        crop = options['crop']
        factors = (geometry[0] / x_image, geometry[1] / y_image)
        return max(factors) if crop else min(factors)

    def scale(self, image, geometry, options):
        """
        Wrapper for ``_scale``
        """
        upscale = options['upscale']
        x_image, y_image = map(float, self.get_image_size(image))
        if self.flip_dimensions(image):
            x_image, y_image = y_image, x_image
        factor = self._calculate_scaling_factor(x_image, y_image, geometry, options)

        if factor < 1 or upscale:
            width = toint(x_image * factor)
            height = toint(y_image * factor)
            image = self._scale(image, width, height)

        return image

    def crop(self, image, geometry, options):
        """
        Wrapper for ``_crop``
        """
        crop = options['crop']
        x_image, y_image = self.get_image_size(image)

        if not crop or crop == 'noop':
            return image
        elif crop == 'smart':
            # Smart cropping is suitably different from regular cropping
            # to warrant it's own function
            return self._entropy_crop(image, geometry[0], geometry[1], x_image, y_image)

        # Handle any other crop option with the backend crop function.
        geometry = (min(x_image, geometry[0]), min(y_image, geometry[1]))
        x_offset, y_offset = parse_crop(crop, (x_image, y_image), geometry)
        return self._crop(image, geometry[0], geometry[1], x_offset, y_offset)

    def rounded(self, image, geometry, options):
        """
        Wrapper for ``_rounded``
        """
        r = options['rounded']
        if not r:
            return image
        return self._rounded(image, int(r))

    def blur(self, image, geometry, options):
        """
        Wrapper for ``_blur``
        """
        if options.get('blur'):
            return self._blur(image, int(options.get('blur')))
        return image

    def padding(self, image, geometry, options):
        """
        Wrapper for ``_padding``
        """
        if options.get('padding') and self.get_image_size(image) != geometry:
            return self._padding(image, geometry, options)
        return image

    def write(self, image, options, thumbnail):
        """
        Wrapper for ``_write``
        """
        format_ = options['format']
        quality = options['quality']
        image_info = options.get('image_info', {})
        # additional non-default-value options:
        progressive = options.get('progressive', settings.THUMBNAIL_PROGRESSIVE)
        raw_data = self._get_raw_data(
            image, format_, quality,
            image_info=image_info,
            progressive=progressive
        )
        thumbnail.write(raw_data)

    def cleanup(self, image):
        """Some backends need to manually cleanup after thumbnails are created"""
        pass

    def get_image_ratio(self, image, options):
        """
        Calculates the image ratio. If cropbox option is used, the ratio
        may have changed.
        """
        cropbox = options['cropbox']

        if cropbox:
            x, y, x2, y2 = parse_cropbox(cropbox)
            x = x2 - x
            y = y2 - y
        else:
            x, y = self.get_image_size(image)

        ratio = float(x) / y

        if self.flip_dimensions(image):
            ratio = 1.0 / ratio

        return ratio

    def get_image_info(self, image):
        """
        Returns metadata of an ImageFile instance
        """
        return {}

    # Methods which engines need to implement
    # The ``image`` argument refers to a backend image object
    def get_image(self, source):
        """
        Returns the backend image objects from an ImageFile instance
        """
        raise NotImplementedError()

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        raise NotImplementedError()

    def is_valid_image(self, raw_data):
        """
        Checks if the supplied raw data is valid image data
        """
        raise NotImplementedError()

    def _orientation(self, image):
        """
        Read orientation exif data and orientate the image accordingly
        """
        return image

    def _colorspace(self, image, colorspace):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        raise NotImplementedError()

    def _remove_border(self, image, image_width, image_height):
        """
        Remove borders around images
        """
        raise NotImplementedError()

    def _entropy_crop(self, image, geometry_width, geometry_height, image_width, image_height):
        """
        Crop the image to the correct aspect ratio
        by removing the lowest entropy parts
        """
        raise NotImplementedError()

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        raise NotImplementedError()

    def _crop(self, image, width, height, x_offset, y_offset):
        """
        Crops the image
        """
        raise NotImplementedError()

    def _get_raw_data(self, image, format_, quality, image_info=None, progressive=False):
        """
        Gets raw data given the image, format and quality. This method is
        called from :meth:`write`
        """
        raise NotImplementedError()

    def _padding(self, image, geometry, options):
        """
        Pads the image
        """
        raise NotImplementedError()

    def _cropbox(self, image, x, y, x2, y2):
        raise NotImplementedError()

    def _rounded(self, image, r):
        raise NotImplementedError()

    def _blur(self, image, radius):
        raise NotImplementedError()
