from django.conf import settings as user_settings
from django.utils.functional import LazyObject
from sorl.thumbnail.conf import defaults


class Settings(object):
    pass


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings()
        for obj in (defaults, user_settings):
            for attr in dir(obj):
                if attr == attr.upper():
                    setattr(self, attr, getattr(obj, attr))


settings = LazySettings()
