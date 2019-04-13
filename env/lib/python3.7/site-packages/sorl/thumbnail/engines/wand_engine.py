'''
Wand (>=v0.3.0) engine for Sorl-thumbnail
'''
from __future__ import unicode_literals

from wand.image import Image
from wand import exceptions
from sorl.thumbnail.engines.base import EngineBase


class Engine(EngineBase):
    def get_image(self, source):
        return Image(blob=source.read())

    def get_image_size(self, image):
        return image.size

    def is_valid_image(self, raw_data):
        '''
        Wand library makes sure when opening any image that is fine, when
        the image is corrupted raises an exception.
        '''

        try:
            Image(blob=raw_data)
            return True
        except (exceptions.CorruptImageError, exceptions.MissingDelegateError):
            return False

    def _orientation(self, image):
        orientation = image.orientation
        if orientation == 'top_right':
            image.flop()
        elif orientation == 'bottom_right':
            image.rotate(degree=180)
        elif orientation == 'bottom_left':
            image.flip()
        elif orientation == 'left_top':
            image.rotate(degree=90)
            image.flop()
        elif orientation == 'right_top':
            image.rotate(degree=90)
        elif orientation == 'right_bottom':
            image.rotate(degree=-90)
            image.flop()
        elif orientation == 'left_bottom':
            image.rotate(degree=-90)
        image.orientation = 'top_left'
        return image

    def _flip_dimensions(self, image):
        return image.orientation in ['left_top', 'right_top', 'right_bottom', 'left_bottom']

    def _colorspace(self, image, colorspace):
        if colorspace == 'RGB':
            if image.alpha_channel:
                image.type = 'truecolormatte'
            else:
                image.type = 'truecolor'
        elif colorspace == 'GRAY':
            if image.alpha_channel:
                image.type = 'grayscalematte'
            else:
                image.type = 'grayscale'
        else:
            return image
        return image

    def _scale(self, image, width, height):
        image.resize(width, height)
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        image.crop(x_offset, y_offset, width=width, height=height)
        return image

    def _get_raw_data(self, image, format_, quality, image_info=None, progressive=False):
        image.compression_quality = quality
        if format_ == 'JPEG' and progressive:
            image.format = 'pjpeg'
        else:
            image.format = format_
        return image.make_blob()
