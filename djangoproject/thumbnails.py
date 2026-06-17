from sorl.thumbnail import get_thumbnail


class LogoThumbnailMixin:
    """
    Add this mixin to a model that has a `logo` ImageField to automatically
    add a `thumbnail` property that will return a (sorl) thumbnail of a standard
    size (available as a constant on the model).
    """

    THUMBNAIL_SIZE = 170

    @property
    def thumbnail(self):
        if self.logo_is_svg:
            return None
        geometry = f"{self.THUMBNAIL_SIZE}x{self.THUMBNAIL_SIZE}"
        return get_thumbnail(self.logo, geometry, quality=100) if self.logo else None

    @property
    def logo_is_svg(self):
        return bool(self.logo) and self.logo.name.lower().endswith(".svg")
