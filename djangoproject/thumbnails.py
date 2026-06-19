from sorl.thumbnail import get_thumbnail


class SVGLogoWrapper:
    def __init__(self, logo):
        self.logo = logo

    @property
    def url(self):
        return self.logo.url

    @property
    def width(self):
        return None

    @property
    def height(self):
        return None

    @property
    def x(self):
        return None

    @property
    def y(self):
        return None

    def exists(self):
        return self.logo.storage.exists(self.logo.name)

    def __str__(self):
        return self.logo.url


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
        if self.logo.name.lower().endswith(".svg"):
            return SVGLogoWrapper(self.logo)
        geometry = f"{self.THUMBNAIL_SIZE}x{self.THUMBNAIL_SIZE}"
        return get_thumbnail(self.logo, geometry, quality=100)
