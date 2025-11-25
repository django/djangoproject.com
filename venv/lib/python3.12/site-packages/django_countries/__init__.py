#!/usr/bin/env python
import itertools
import re
from contextlib import contextmanager
from gettext import NullTranslations
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
    overload,
)

from asgiref.local import Local
from django.utils.encoding import force_str
from django.utils.translation import override, trans_real
from typing_extensions import Literal, TypedDict

from django_countries.conf import settings

from .base import CountriesBase

if TYPE_CHECKING:
    from django_stubs_ext import StrPromise

try:
    import pyuca  # type: ignore

    collator = pyuca.Collator()

    # Use UCA sorting if it's available.
    def sort_key(item: Tuple[str, str]) -> Any:
        return collator.sort_key(item[1])

except ImportError:
    # Fallback if the UCA sorting is not available.
    import unicodedata

    # Cheap and dirty method to sort against ASCII characters only.
    def sort_key(item: Tuple[str, str]) -> Any:
        return (
            unicodedata.normalize("NFKD", item[1])
            .encode("ascii", "ignore")
            .decode("ascii")
        )


_translation_state = Local()


class EmptyFallbackTranslator(NullTranslations):
    def gettext(self, message: str) -> str:
        if not getattr(_translation_state, "fallback", True):
            # Interrupt the fallback chain.
            return ""
        return super().gettext(message)


@contextmanager
def no_translation_fallback():
    if not settings.USE_I18N:
        yield
        return
    # Ensure the empty fallback translator has been installed.
    catalog = trans_real.catalog()
    original_fallback = catalog._fallback
    if not isinstance(original_fallback, EmptyFallbackTranslator):
        empty_fallback_translator = EmptyFallbackTranslator()
        empty_fallback_translator._fallback = original_fallback
        catalog._fallback = empty_fallback_translator
    # Set the translation state to not use a fallback while inside this context.
    _translation_state.fallback = False
    try:
        yield
    finally:
        _translation_state.fallback = True


class ComplexCountryName(TypedDict):
    name: "StrPromise"
    names: "List[StrPromise]"
    alpha3: str
    numeric: int
    ioc_code: str


CountryName = Union["StrPromise", ComplexCountryName]
CountryCode = Union[str, int, None]


class AltCodes(NamedTuple):
    alpha3: str
    numeric: Optional[int]


class CountryTuple(NamedTuple):
    code: str
    name: str

    def __repr__(self) -> str:
        """
        Display the repr as a standard tuple for better backwards
        compatibility with outputting this in a template.
        """
        return f"({self.code!r}, {self.name!r})"


class Countries(CountriesBase):
    """
    An object containing a list of ISO3166-1 countries.

    Iterating this object will return the countries as namedtuples (of
    the country ``code`` and ``name``), sorted by name.
    """

    _countries: Dict[str, CountryName]
    _alt_codes: Dict[str, AltCodes]

    def get_option(self, option: str):
        """
        Get a configuration option, trying the options attribute first and
        falling back to a Django project setting.
        """
        value = getattr(self, option, None)
        if value is not None:
            return value
        return getattr(settings, f"COUNTRIES_{option.upper()}")

    @property
    def countries(self) -> Dict[str, CountryName]:
        """
        Return the a dictionary of countries, modified by any overriding
        options.

        The result is cached so future lookups are less work intensive.
        """
        if not hasattr(self, "_countries"):
            only: "Iterable[Union[str, Tuple[str, StrPromise]]]" = self.get_option(
                "only"
            )
            only_choices = True
            if only:
                # Originally used ``only`` as a dict, still supported.
                if not isinstance(only, dict):
                    for item in only:
                        if isinstance(item, str):
                            only_choices = False
                            break
            self._shadowed_names: "Dict[str, List[StrPromise]]" = {}
            if only and only_choices:
                self._countries = dict(only)  # type: ignore
            else:
                # Local import so that countries aren't loaded into memory
                # until first used.
                from django_countries.data import COUNTRIES

                countries_dict = dict(COUNTRIES)
                if only:
                    self._countries = {}
                    for item in only:
                        if isinstance(item, str):
                            self._countries[item] = countries_dict[item]
                        else:
                            key, value = item
                            self._countries[key] = value
                else:
                    self._countries = countries_dict.copy()  # type: ignore
                if self.get_option("common_names"):
                    for code, name in self.COMMON_NAMES.items():
                        if code in self._countries:
                            self._countries[code] = name
                override: Dict[str, Union[CountryName, None]] = self.get_option(
                    "override"
                )
                if override:
                    _countries = cast(
                        Dict[str, Union[CountryName, None]], self._countries.copy()
                    )
                    _countries.update(override)
                    self._countries = {
                        code: name
                        for code, name in _countries.items()
                        if name is not None
                    }

                if self.get_option("common_names"):
                    for code in self.COMMON_NAMES:
                        if code in self._countries and code not in override:
                            self._shadowed_names[code] = [countries_dict[code]]
                for code, names in self.OLD_NAMES.items():
                    if code in self._countries and code not in override:
                        country_shadowed = self._shadowed_names.setdefault(code, [])
                        country_shadowed.extend(names)

            self.countries_first = []
            first: List[str] = self.get_option("first") or []
            for code in first:
                code = self.alpha2(code)
                if code in self._countries:
                    self.countries_first.append(code)
        return self._countries

    @countries.deleter
    def countries(self):
        """
        Reset the countries cache in case for some crazy reason the settings or
        internal options change. But surely no one is crazy enough to do that,
        right?
        """
        if hasattr(self, "_countries"):
            del self._countries
        if hasattr(self, "_alt_codes"):
            del self._alt_codes
        if hasattr(self, "_ioc_codes"):
            del self._ioc_codes
        if hasattr(self, "_shadowed_names"):
            del self._shadowed_names

    @property
    def alt_codes(self) -> Dict[str, AltCodes]:
        if not hasattr(self, "_alt_codes"):
            # Again, local import so data is not loaded unless it's needed.
            from django_countries.data import ALT_CODES

            self._alt_codes = ALT_CODES  # type: ignore
            altered = False
            for code, country in self.countries.items():
                if isinstance(country, dict) and (
                    "alpha3" in country or "numeric" in country
                ):
                    if not altered:
                        self._alt_codes = self._alt_codes.copy()
                        altered = True
                    alpha3, numeric = self._alt_codes.get(code, ("", None))
                    if "alpha3" in country:
                        alpha3 = country["alpha3"]
                    if "numeric" in country:
                        numeric = country["numeric"]
                    self._alt_codes[code] = AltCodes(alpha3, numeric)
        return self._alt_codes

    @property
    def ioc_codes(self) -> Dict[str, str]:
        if not hasattr(self, "_ioc_codes"):
            from django_countries.ioc_data import ISO_TO_IOC

            self._ioc_codes = ISO_TO_IOC
            altered = False
            for code, country in self.countries.items():
                if isinstance(country, dict) and "ioc_code" in country:
                    if not altered:
                        self._ioc_codes = self._ioc_codes.copy()
                        altered = True
                    self._ioc_codes[code] = country["ioc_code"]
        return self._ioc_codes

    @property
    def shadowed_names(self):
        if not getattr(self, "_shadowed_names", False):
            # Getting countries populates shadowed names.
            self.countries
        return self._shadowed_names

    def translate_code(self, code: str, ignore_first: Optional[List[str]] = None):
        """
        Return translated countries for a country code.
        """
        country = self.countries[code]
        if isinstance(country, dict):
            if "names" in country:
                names = country["names"]
            else:
                names = [country["name"]]
        else:
            names = [country]
        if ignore_first and code in ignore_first:
            names = names[1:]
        for name in names:
            yield self.translate_pair(code, name)

    def translate_pair(self, code: str, name: Optional[CountryName] = None):
        """
        Force a country to the current activated translation.

        :returns: ``CountryTuple(code, translated_country_name)`` namedtuple
        """
        if name is None:
            name = self.countries[code]
        if isinstance(name, dict):
            if "names" in name:
                fallback_names: "List[StrPromise]" = name["names"][1:]
                name = name["names"][0]
            else:
                fallback_names = []
                name = name["name"]
        else:
            fallback_names = self.shadowed_names.get(code, [])
        if fallback_names:
            with no_translation_fallback():
                country_name = force_str(name)
                # Check if there's an older translation available if there's no
                # translation for the newest name.
                if not country_name:
                    for fallback_name in fallback_names:
                        fallback_name_str = force_str(fallback_name)
                        if fallback_name_str:
                            country_name = fallback_name_str
                            break
            if not country_name:
                # Use the translation's fallback country name.
                country_name = force_str(name)
        else:
            country_name = force_str(name)
        return CountryTuple(code, country_name)

    def __iter__(self):
        """
        Iterate through countries, sorted by name.

        Each country record consists of a namedtuple of the two letter
        ISO3166-1 country ``code`` and short ``name``.

        The sorting happens based on the thread's current translation.

        Countries that are in ``settings.COUNTRIES_FIRST`` will be
        displayed before any sorted countries (in the order provided),
        and are only repeated in the sorted list if
        ``settings.COUNTRIES_FIRST_REPEAT`` is ``True``.

        The first countries can be separated from the sorted list by the
        value provided in ``settings.COUNTRIES_FIRST_BREAK``.
        """
        # Initializes countries_first, so needs to happen first.
        countries = self.countries

        # Yield countries that should be displayed first.
        countries_first = (self.translate_pair(code) for code in self.countries_first)

        if self.get_option("first_sort"):
            countries_first = sorted(countries_first, key=sort_key)

        yield from countries_first

        if self.countries_first:
            first_break = self.get_option("first_break")
            if first_break:
                yield CountryTuple("", force_str(first_break))

        # Force translation before sorting.
        ignore_first = None if self.get_option("first_repeat") else self.countries_first
        countries = tuple(
            itertools.chain.from_iterable(
                self.translate_code(code, ignore_first) for code in countries
            )
        )

        # Return sorted country list.
        yield from sorted(countries, key=sort_key)

    def alpha2(self, code: CountryCode) -> str:
        """
        Return the normalized country code when passed any type of ISO 3166-1
        country code.

        Overridden countries objects may actually have country codes that are
        not two characters (for example, "GB-WLS"), so the returned length of
        the code is not guaranteed.

        If no match is found, returns an empty string.
        """
        find: Optional[Callable]
        code_str = force_str(code).upper()
        if code_str.isdigit():
            lookup_numeric = int(code_str)

            def find(alt_codes):
                return alt_codes[1] == lookup_numeric

        elif len(code_str) == 3:
            lookup_alpha3 = code_str

            def find(alt_codes) -> bool:
                return alt_codes[0] == lookup_alpha3

        else:
            find = None
        if find:
            code_str = ""
            for alpha2, alt_codes in self.alt_codes.items():
                if find(alt_codes):
                    code_str = alpha2
                    break
        if code_str in self.countries:
            return code_str
        return ""

    def name(self, code: CountryCode) -> str:
        """
        Return the name of a country, based on the code.

        If no match is found, returns an empty string.
        """
        alpha2 = self.alpha2(code)
        if alpha2 not in self.countries:
            return ""
        return self.translate_pair(alpha2)[1]

    @overload
    def by_name(
        self,
        country: str,
        *,
        regex: Literal[False] = False,
        language: str = "en",
        insensitive: bool = True,
    ) -> str:
        ...

    @overload
    def by_name(
        self,
        country: str,
        *,
        regex: Literal[True],
        language: str = "en",
        insensitive: bool = True,
    ) -> Set[str]:
        ...

    def by_name(
        self,
        country: str,
        *,
        regex: bool = False,
        language: str = "en",
        insensitive: bool = True,
    ) -> Union[str, Set[str]]:
        """
        Fetch a country's ISO3166-1 two letter country code from its name.

        An optional language parameter is also available. Warning: This depends
        on the quality of the available translations.

        If no match is found, returns an empty string.

        If ``regex`` is set to True, then rather than returning a string
        containing the matching country code or an empty string, a set of
        matching country codes is returned.

        If ``insensitive`` is set to False (True by default), then the search
        will be case sensitive.

        ..warning:: Be cautious about relying on this returning a country code
            (especially with any hard-coded string) since the ISO names of
            countries may change over time.
        """
        code_list = set()
        if regex:
            re_match = re.compile(country, insensitive and re.IGNORECASE)
        elif insensitive:
            country = country.lower()
        with override(language):
            for code, check_country in self.countries.items():
                if isinstance(check_country, dict):
                    if "names" in check_country:
                        check_names: "List[StrPromise]" = check_country["names"]
                    else:
                        check_names = [check_country["name"]]
                else:
                    check_names = [check_country]
                for name in check_names:
                    if regex:
                        if re_match.search(str(name)):
                            code_list.add(code)
                    else:
                        if insensitive:
                            if country == name.lower():
                                return code
                        else:
                            if country == name:
                                return code
                if code in self.shadowed_names:
                    for shadowed_name in self.shadowed_names[code]:
                        if regex:
                            if re_match.search(str(shadowed_name)):
                                code_list.add(code)
                        else:
                            if insensitive:
                                shadowed_name = shadowed_name.lower()
                            if country == shadowed_name:
                                return code
        if regex:
            return code_list
        return ""

    def alpha3(self, code: CountryCode) -> str:
        """
        Return the ISO 3166-1 three letter country code matching the provided
        country code.

        If no match is found, returns an empty string.
        """
        alpha2 = self.alpha2(code)
        try:
            alpha3 = self.alt_codes[alpha2][0]
        except KeyError:
            alpha3 = ""
        return alpha3 or ""

    @overload
    def numeric(
        self, code: Union[str, int, None], padded: Literal[False] = False
    ) -> Optional[int]:
        ...

    @overload
    def numeric(
        self, code: Union[str, int, None], padded: Literal[True]
    ) -> Optional[str]:
        ...

    def numeric(self, code: Union[str, int, None], padded: bool = False):
        """
        Return the ISO 3166-1 numeric country code matching the provided
        country code.

        If no match is found, returns ``None``.

        :param padded: Pass ``True`` to return a 0-padded three character
            string, otherwise an integer will be returned.
        """
        alpha2 = self.alpha2(code)
        try:
            num = self.alt_codes[alpha2][1]
        except KeyError:
            num = None
        if num is None:
            return None
        if padded:
            return "%03d" % num
        return num

    def ioc_code(self, code: CountryCode) -> str:
        """
        Return the International Olympic Committee three letter code matching
        the provided ISO 3166-1 country code.

        If no match is found, returns an empty string.
        """
        alpha2 = self.alpha2(code)
        return self.ioc_codes.get(alpha2, "")

    def __len__(self):
        """
        len() used by several third party applications to calculate the length
        of choices. This will solve a bug related to generating fixtures.
        """
        count = len(self.countries)
        # Add first countries, and the break if necessary.
        count += len(self.countries_first)
        if self.countries_first and self.get_option("first_break"):
            count += 1
        return count

    def __bool__(self):
        return bool(self.countries)

    def __contains__(self, code):
        """
        Check to see if the countries contains the given code.
        """
        return code in self.countries

    def __getitem__(self, index):
        """
        Some applications expect to be able to access members of the field
        choices by index.
        """
        try:
            return next(itertools.islice(self.__iter__(), index, index + 1))
        except TypeError:
            return list(
                itertools.islice(self.__iter__(), index.start, index.stop, index.step)
            )


countries = Countries()
