import copy
from typing import List, Union
from urllib import parse as urlparse

import django
from django.forms import widgets
from django.utils.functional import Promise
from django.utils.html import escape
from django.utils.safestring import mark_safe

from django_countries.conf import settings

COUNTRY_CHANGE_HANDLER = (
    "var e=document.getElementById('flag_' + this.id); "
    "if (e) e.src = '%s'"
    ".replace('{code}', this.value.toLowerCase() || '__')"
    ".replace('{code_upper}', this.value.toUpperCase() || '__');"
)

ChoiceList = List[List[Union[int, str]]]


class LazyChoicesMixin:
    if django.VERSION < (5, 0):

        def get_choices(self) -> ChoiceList:
            """
            When it's time to get the choices, if it was a lazy then figure it out
            now and memoize the result.
            """
            if isinstance(self._choices, Promise):
                self._choices: ChoiceList = list(self._choices)
            return self._choices

        def set_choices(self, value: ChoiceList):
            self._set_choices(value)

        choices = property(get_choices, set_choices)

        def _set_choices(self, value: ChoiceList):
            self._choices = value


class LazySelectMixin(LazyChoicesMixin):
    if django.VERSION < (5, 0):

        def __deepcopy__(self, memo):
            obj = copy.copy(self)
            obj.attrs = self.attrs.copy()
            obj.choices = copy.copy(self._choices)
            memo[id(self)] = obj
            return obj


class LazySelect(LazySelectMixin, widgets.Select):  # type: ignore
    """
    A form Select widget that respects choices being a lazy object.
    """


class LazySelectMultiple(LazySelectMixin, widgets.SelectMultiple):  # type: ignore
    """
    A form SelectMultiple widget that respects choices being a lazy object.
    """


class CountrySelectWidget(LazySelect):
    def __init__(self, *args, **kwargs) -> None:
        self.layout = kwargs.pop("layout", None) or (
            '{widget}<img class="country-select-flag" id="{flag_id}" '
            'style="margin: 6px 4px 0" '
            'src="{country.flag}">'
        )
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from django_countries.fields import Country

        attrs = attrs or {}
        widget_id = attrs and attrs.get("id")
        if widget_id:
            flag_id = f"flag_{widget_id}"
            attrs["onchange"] = COUNTRY_CHANGE_HANDLER % urlparse.urljoin(
                settings.STATIC_URL, settings.COUNTRIES_FLAG_URL
            )
        else:
            flag_id = ""
        widget_render = super().render(name, value, attrs, renderer=renderer)
        country = value if isinstance(value, Country) else Country(value or "__")
        with country.escape:
            return mark_safe(  # nosec
                self.layout.format(
                    widget=widget_render, country=country, flag_id=escape(flag_id)
                )
            )
