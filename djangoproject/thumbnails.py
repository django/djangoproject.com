import logging

from sorl.thumbnail import get_thumbnail

logger = logging.getLogger(__name__)


class LogoThumbnailMixin:
    """
    Add this mixin to a model that has a `logo` ImageField to automatically
    add a `thumbnail` property that will return a (sorl) thumbnail of a standard
    size (available as a constant on the model).
    """

    THUMBNAIL_SIZE = 170

    @property
    def thumbnail(self):
        if not self.logo:
            return None
        if self.logo_is_svg:
            return None
        geometry = f"{self.THUMBNAIL_SIZE}x{self.THUMBNAIL_SIZE}"
        try:
            return get_thumbnail(self.logo, geometry, quality=100)
        except Exception:
            logger.warning("Could not thumbnail logo %r", self.logo.name)
        return None

    @property
    def logo_is_svg(self):
        return bool(self.logo) and self.logo.name.lower().endswith(".svg")
