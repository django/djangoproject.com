import re
import sys
from typing import Any, Iterable, Optional, Tuple, Type, Union, cast
from urllib import parse as urlparse

import django
from django import forms
from django.contrib.admin.filters import FieldListFilter
from django.core import checks, exceptions
from django.db.models import lookups
from django.db.models.fields import BLANK_CHOICE_DASH, CharField
from django.utils.encoding import force_str
from django.utils.functional import lazy
from django.utils.html import escape as escape_html

from django_countries import Countries, countries, filters, ioc_data, widgets
from django_countries.conf import settings

_entry_points: Iterable[Any]
try:
    import importlib.metadata

    if sys.version_info >= (3, 10):
        _entry_points = importlib.metadata.entry_points(
            group="django_countries.Country"
        )
    else:
        _entry_points = importlib.metadata.entry_points().get(
            "django_countries.Country", []
        )
except ImportError:  # Python <3.8
    import pkg_resources

    _entry_points = pkg_resources.iter_entry_points("django_countries.Country")

EXTENSIONS = {ep.name: ep.load() for ep in _entry_points}  # type: ignore


class TemporaryEscape:
    __slots__ = ["country", "original_escape"]

    def __init__(self, country):
        self.country = country

    def __bool__(self):
        return self.country._escape

    def __enter__(self):
        self.original_escape = self.country._escape
        self.country._escape = True

    def __exit__(self, type, value, traceback):
        self.country._escape = self.original_escape


class Country:
    def __init__(
        self,
        code: str,
        flag_url: Optional[str] = None,
        str_attr: str = "code",
        custom_countries: Optional[Countries] = None,
    ):
        self.flag_url = flag_url
        self._escape = False
        self._str_attr = str_attr
        if custom_countries is countries:
            custom_countries = None
        self.custom_countries = custom_countries
        # Attempt to convert the code to the alpha2 equivalent, but this
        # is not meant to be full validation so use the given code if no
        # match was found.
        self.code = self.countries.alpha2(code) or code

    def __str__(self):
        return force_str(getattr(self, self._str_attr) or "")

    def __eq__(self, other):
        return force_str(self.code or "") == force_str(other or "")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(force_str(self))

    def __repr__(self):
        args = [f"code={self.code!r}"]
        if self.flag_url is not None:
            args.append(f"flag_url={self.flag_url!r}")
        if self._str_attr != "code":
            args.append(f"str_attr={self._str_attr!r}")
        return f"{self.__class__.__name__}({', '.join(args)})"

    def __bool__(self):
        return bool(self.code)

    def __len__(self):
        return len(force_str(self))

    @property
    def countries(self):
        return self.custom_countries or countries

    @property
    def escape(self):
        return TemporaryEscape(self)

    def maybe_escape(self, text) -> str:
        return escape_html(text) if self.escape else text

    @property
    def name(self) -> str:
        return self.maybe_escape(self.countries.name(self.code))

    @property
    def alpha3(self) -> str:
        return self.countries.alpha3(self.code)

    @property
    def numeric(self) -> Optional[int]:
        return self.countries.numeric(self.code)

    @property
    def numeric_padded(self) -> Optional[str]:
        return self.countries.numeric(self.code, padded=True)

    @property
    def flag(self) -> str:
        if not self.code:
            return ""
        flag_url = self.flag_url
        if flag_url is None:
            flag_url = settings.COUNTRIES_FLAG_URL
        url = flag_url.format(code_upper=self.code, code=self.code.lower())
        if not url:
            return ""
        url = urlparse.urljoin(settings.STATIC_URL, url)
        return self.maybe_escape(url)

    @property
    def flag_css(self) -> str:
        """
        Output the css classes needed to display an HTML element as a flag
        sprite.

        Requires the use of 'flags/sprite.css' or 'flags/sprite-hq.css'.
        Usage example::

            <i class="{{ ctry.flag_css }}" aria-label="{{ ctry.code }}></i>
        """
        if not self.code:
            return ""
        x, y = list(self.code.lower())
        return f"flag-sprite flag-{x} flag-_{y}"

    @property
    def unicode_flag(self):
        """
        Generate a unicode flag for the given country.

        The logic for how these are determined can be found at:

        https://en.wikipedia.org/wiki/Regional_Indicator_Symbol

        Currently, these glyphs appear to only be supported on OS X and iOS.
        """
        if not self.code:
            return ""

        # Don't really like magic numbers, but this is the code point for [A]
        # (Regional Indicator A), minus the code point for ASCII A. By adding
        # this to the uppercase characters making up the ISO 3166-1 alpha-2
        # codes we can get the flag.
        OFFSET = 127397
        points = [ord(x) + OFFSET for x in self.code.upper()]
        return chr(points[0]) + chr(points[1])

    @staticmethod
    def country_from_ioc(ioc_code, flag_url=""):
        code = ioc_data.IOC_TO_ISO.get(ioc_code, "")
        if code == "":
            return None
        return Country(code, flag_url=flag_url)

    @property
    def ioc_code(self):
        return self.countries.ioc_code(self.code)

    def __getattr__(self, attr):
        if attr in EXTENSIONS:
            return EXTENSIONS[attr](self)
        raise AttributeError()


class CountryDescriptor:
    """
    A descriptor for country fields on a model instance. Returns a Country when
    accessed so you can do things like::

        >>> from people import Person
        >>> person = Person.object.get(name='Chris')

        >>> person.country.name
        'New Zealand'

        >>> person.country.flag
        '/static/flags/nz.gif'
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            return self
        # Check in case this field was deferred.
        if self.field.name not in instance.__dict__:
            instance.refresh_from_db(fields=[self.field.name])
        value = instance.__dict__[self.field.name]
        if self.field.multiple:
            return [self.country(code) for code in value]
        return self.country(value)

    def country(self, code):
        return Country(
            code=code,
            flag_url=self.field.countries_flag_url,
            str_attr=self.field.countries_str_attr,
            custom_countries=self.field.countries,
        )

    def __set__(self, instance, value):
        value = self.field.get_clean_value(value)
        instance.__dict__[self.field.name] = value


class LazyChoicesMixin(widgets.LazyChoicesMixin):
    if django.VERSION < (5, 0):

        def _set_choices(self, value):
            """
            Also update the widget's choices.
            """
            super()._set_choices(value)
            self.widget.choices = value


_Choice = Tuple[Any, str]
_ChoiceNamedGroup = Tuple[str, Iterable[_Choice]]
_FieldChoices = Iterable[Union[_Choice, _ChoiceNamedGroup]]


class LazyTypedChoiceField(LazyChoicesMixin, forms.TypedChoiceField):
    """
    A form TypedChoiceField that respects choices being a lazy object.
    """

    choices: Any
    widget = widgets.LazySelect


class LazyTypedMultipleChoiceField(LazyChoicesMixin, forms.TypedMultipleChoiceField):
    """
    A form TypedMultipleChoiceField that respects choices being a lazy object.
    """

    choices: Any
    widget = widgets.LazySelectMultiple


class CountryField(CharField):
    """
    A country field for Django models that provides all ISO 3166-1 countries as
    choices.
    """

    descriptor_class = CountryDescriptor
    countries: Countries

    def __init__(self, *args: Any, **kwargs: Any):
        countries_class: Type[Countries] = kwargs.pop("countries", None)
        self.countries = countries_class() if countries_class else countries
        self.countries_flag_url = kwargs.pop("countries_flag_url", None)
        self.countries_str_attr = kwargs.pop("countries_str_attr", "code")
        self.blank_label = kwargs.pop("blank_label", None)
        self.multiple = kwargs.pop("multiple", None)
        self.multiple_unique = kwargs.pop("multiple_unique", True)
        self.multiple_sort = kwargs.pop("multiple_sort", True)
        if django.VERSION >= (5, 0):
            # Use new lazy callable support
            kwargs["choices"] = lambda: self.countries
        else:
            kwargs["choices"] = self.countries
        if "max_length" not in kwargs:
            # Allow explicit max_length so migrations can correctly identify
            # changes in the multiple CountryField fields when new countries are
            # added to the available countries dictionary.
            if self.multiple:
                kwargs["max_length"] = (
                    len(self.countries)
                    - 1
                    + sum(len(code) for code in self.countries.countries)
                )
            else:
                kwargs["max_length"] = max(
                    len(code) for code in self.countries.countries
                )
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_multiple())
        return errors

    def _check_multiple(self):
        if not self.multiple or not self.null:
            return []

        hint = "Remove null=True argument on the field"
        if not self.blank:
            hint += " (just add blank=True if you want to allow no selection)"
        hint += "."

        return [
            checks.Error(
                "Field specifies multiple=True, so should not be null.",
                obj=self,
                id="django_countries.E100",
                hint=hint,
            )
        ]

    def get_internal_type(self):
        return "CharField"

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        setattr(cls, self.name, self.descriptor_class(self))

    def pre_save(self, *args, **kwargs):
        "Returns field's value just before saving."
        value = super(CharField, self).pre_save(*args, **kwargs)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        value = self.get_clean_value(value)
        if self.multiple:
            value = ",".join(value) if value else ""
        return super(CharField, self).get_prep_value(value)

    def country_to_text(self, value):
        if hasattr(value, "code"):
            value = value.code
        if value is None:
            return None
        return force_str(value)

    def get_clean_value(self, value):
        if value is None:
            return None
        if not self.multiple:
            return self.country_to_text(value)
        if isinstance(value, (str, Country)):
            if isinstance(value, str) and "," in value:
                value = value.split(",")
            else:
                value = [value]
        else:
            try:
                iter(value)
            except TypeError:
                value = [value]
        cleaned_value = []
        seen = set()
        for c in value:
            c = self.country_to_text(c)
            if not c:
                continue
            if self.multiple_unique:
                if c in seen:
                    continue
                seen.add(c)
            cleaned_value.append(c)
        if self.multiple_sort:
            cleaned_value = sorted(cleaned_value)
        return cleaned_value

    def deconstruct(self):
        """
        Remove choices from deconstructed field, as this is the country list
        and not user editable.

        Not including the ``blank_label`` property, as this isn't database
        related.
        """
        name, path, args, kwargs = super(CharField, self).deconstruct()
        kwargs.pop("choices", None)
        if self.multiple:  # multiple determines the length of the field
            kwargs["multiple"] = self.multiple
        if not self.multiple_unique:
            kwargs["multiple_unique"] = False
        if not self.multiple_sort:
            kwargs["multiple_sort"] = False
        if self.countries is not countries:
            # Include the countries class if it's not the default countries
            # instance.
            kwargs["countries"] = self.countries.__class__
        return name, path, args, kwargs

    if django.VERSION >= (5, 0):

        def get_choices(
            self,
            include_blank=True,
            blank_choice=BLANK_CHOICE_DASH,
            limit_choices_to=None,
            ordering=(),
        ):
            if self.multiple:
                include_blank = False
            if self.blank_label is None:
                blank_choice = BLANK_CHOICE_DASH
            else:
                blank_choice = [("", self.blank_label)]
            return super().get_choices(
                include_blank=include_blank,
                blank_choice=blank_choice,
                limit_choices_to=limit_choices_to,
                ordering=ordering,
            )

    else:

        def get_choices(  # type: ignore [misc]
            self, include_blank=True, blank_choice=None, *args, **kwargs
        ):
            if blank_choice is None:
                if self.blank_label is None:
                    blank_choice = BLANK_CHOICE_DASH
                else:
                    blank_choice = [("", self.blank_label)]
            if self.multiple:
                include_blank = False
            return super().get_choices(
                include_blank=include_blank, blank_choice=blank_choice, *args, **kwargs
            )

        get_choices = lazy(get_choices, list)

    def formfield(self, **kwargs):
        kwargs.setdefault(
            "choices_form_class",
            LazyTypedMultipleChoiceField if self.multiple else LazyTypedChoiceField,
        )
        if "coerce" not in kwargs:
            kwargs["coerce"] = super().to_python
        return super().formfield(**kwargs)

    def to_python(self, value):
        if not self.multiple:
            return super().to_python(value)
        if not value:
            return value
        if isinstance(value, str):
            value = value.split(",")
        output = []
        for item in value:
            output.append(super().to_python(item))
        return output

    def validate(self, value, model_instance):
        """
        Use custom validation for when using a multiple countries field.
        """
        if not self.multiple:
            return super().validate(value, model_instance)

        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if value:
            choices = [option_key for option_key, option_value in self.choices]
            for single_value in value:
                if single_value not in choices:
                    raise exceptions.ValidationError(
                        self.error_messages["invalid_choice"],
                        code="invalid_choice",
                        params={"value": single_value},
                    )

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages["blank"], code="blank")

    def value_to_string(self, obj):
        """
        Ensure data is serialized correctly.
        """
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def get_lookup(self, lookup_name):
        if not self.multiple and lookup_name in (
            "contains",
            "icontains",
            "startswith",
            "istartswith",
            "endswith",
            "iendswith",
            "regex",
            "iregex",
            "name",
            "iname",
        ):
            lookup_name = f"country_{lookup_name}"
        return super().get_lookup(lookup_name)


@CountryField.register_lookup
class ExactNameLookup(lookups.Exact):
    lookup_name = "country_name"
    insensitive: bool = False

    def get_prep_lookup(self):
        return cast(CountryField, self.lhs.output_field).countries.by_name(
            force_str(self.rhs), insensitive=self.insensitive
        )

    def get_rhs_op(self, connection, rhs):
        return connection.operators["exact"] % rhs


@CountryField.register_lookup
class IExactNameLookup(ExactNameLookup):
    lookup_name = "country_iname"
    insensitive: bool = True


class FullNameLookup(lookups.In):
    expr: str
    insensitive: bool = False
    escape_regex: bool = True

    def get_prep_lookup(self):
        if isinstance(self.rhs, str):
            value = self.expr.format(
                text=re.escape(self.rhs) if self.escape_regex else self.rhs
            )
            options = cast(CountryField, self.lhs.output_field).countries.by_name(
                value, regex=True, insensitive=self.insensitive
            )
            if len(self.rhs) == 2 and (
                self.rhs == self.rhs.upper() or self.insensitive
            ):
                options.add(self.rhs.upper())
            return options
        return super().get_prep_lookup()  # pragma: no cover


@CountryField.register_lookup
class CountryContains(FullNameLookup):
    lookup_name = "country_contains"
    expr = r"{text}"


@CountryField.register_lookup
class CountryIContains(CountryContains):
    lookup_name = "country_icontains"
    insensitive = True


@CountryField.register_lookup
class CountryStartswith(FullNameLookup):
    lookup_name = "country_startswith"
    expr = r"^{text}"


@CountryField.register_lookup
class CountryIStartswith(CountryStartswith):
    lookup_name = "country_istartswith"
    insensitive = True


@CountryField.register_lookup
class CountryEndswith(FullNameLookup):
    lookup_name = "country_endswith"
    expr = r"{text}$"


@CountryField.register_lookup
class CountryIEndswith(CountryEndswith):
    lookup_name = "country_iendswith"
    insensitive = True


@CountryField.register_lookup
class CountryRegex(FullNameLookup):
    lookup_name = "country_regex"
    expr = r"{text}"
    escape_regex = False


@CountryField.register_lookup
class CountryIRegex(CountryRegex):
    lookup_name = "country_iregex"
    insensitive = True


FieldListFilter.register(lambda f: isinstance(f, CountryField), filters.CountryFilter)
