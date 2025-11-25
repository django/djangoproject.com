from django.conf import settings as user_settings

from sorl.thumbnail.conf import defaults


class Settings:
    """
    Settings proxy that will lookup first in the django settings, and then in the conf
    defaults.
    """
    def __getattr__(self, name):
        if name != name.upper():
            raise AttributeError(name)
        try:
            return getattr(user_settings, name)
        except AttributeError:
            return getattr(defaults, name)


settings = Settings()
