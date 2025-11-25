import pytest
from django.test import TestCase
from django.utils import translation

from django_countries import Countries, CountryTuple, countries
from django_countries.conf import settings
from django_countries.tests import custom_countries

EXPECTED_COUNTRY_COUNT = 249
FIRST_THREE_COUNTRIES = [
    ("AF", "Afghanistan"),
    ("AX", "Åland Islands"),
    ("AL", "Albania"),
]


class BaseTest(TestCase):
    def setUp(self):
        del countries.countries

    def tearDown(self):
        del countries.countries


class TestCountriesObject(BaseTest):
    def test_countries_len(self):
        self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT)

    def test_countries_sorted(self):
        self.assertEqual(list(countries)[:3], FIRST_THREE_COUNTRIES)

    def test_countries_namedtuple(self):
        country = list(countries)[0]
        first_country = FIRST_THREE_COUNTRIES[0]
        self.assertEqual(country.code, first_country[0])
        self.assertEqual(country.name, first_country[1])
        self.assertIsInstance(country, CountryTuple)

    def test_countries_limit(self):
        with self.settings(COUNTRIES_ONLY={"NZ": "New Zealand", "NV": "Neverland"}):
            self.assertEqual(
                list(countries), [("NV", "Neverland"), ("NZ", "New Zealand")]
            )
            self.assertEqual(len(countries), 2)

    def test_countries_limit_codes(self):
        with self.settings(COUNTRIES_ONLY=["NZ", ("NV", "Neverland")]):
            self.assertEqual(
                list(countries), [("NV", "Neverland"), ("NZ", "New Zealand")]
            )
            self.assertEqual(len(countries), 2)

    def test_countries_custom_removed_len(self):
        with self.settings(COUNTRIES_OVERRIDE={"AU": None}):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT - 1)

    def test_countries_custom_added_len(self):
        with self.settings(COUNTRIES_OVERRIDE={"XX": "Neverland"}):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT + 1)

    def test_countries_getitem(self):
        countries[0]

    def test_countries_slice(self):
        sliced = countries[10:20:2]
        self.assertEqual(len(sliced), 5)

    def test_countries_custom_gettext_evaluation(self):
        class FakeLazyGetText:
            def __bool__(self):  # pragma: no cover
                raise ValueError("Can't evaluate lazy_gettext yet")

        with self.settings(COUNTRIES_OVERRIDE={"AU": FakeLazyGetText()}):
            countries.countries

    def test_ioc_countries(self):
        from ..ioc_data import check_ioc_countries

        check_ioc_countries(verbosity=0)

    def test_initial_iter(self):
        # Use a new instance so nothing is cached
        dict(Countries())

    def test_flags(self):
        from ..data import check_flags

        check_flags(verbosity=0)

    def test_common_names(self):
        from ..data import check_common_names

        check_common_names()

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_common_name_translation(self):
        lang = translation.get_language()
        translation.activate("de")
        try:
            self.assertEqual(countries.name("BO"), "Bolivien")
            self.assertEqual(countries.name("VE"), "Venezuela")
        finally:
            translation.activate(lang)

    def test_alpha2(self):
        self.assertEqual(countries.alpha2("NZ"), "NZ")
        self.assertEqual(countries.alpha2("nZ"), "NZ")
        self.assertEqual(countries.alpha2("Nzl"), "NZ")
        self.assertEqual(countries.alpha2(554), "NZ")
        self.assertEqual(countries.alpha2("554"), "NZ")

    def test_alpha2_invalid(self):
        self.assertEqual(countries.alpha2("XX"), "")

    def test_alpha2_override(self):
        with self.settings(COUNTRIES_OVERRIDE={"AU": None}):
            self.assertEqual(countries.alpha2("AU"), "")

    def test_alpha3_override(self):
        with self.settings(
            COUNTRIES_OVERRIDE={
                "AU": None,
                "NZ": {"alpha3": ""},
                "US": {"alpha3": "XXX"},
            }
        ):
            self.assertEqual(countries.alpha3("AU"), "")
            self.assertEqual(countries.alpha3("NZ"), "")
            self.assertEqual(countries.alpha3("US"), "XXX")

    def test_numeric_override(self):
        with self.settings(
            COUNTRIES_OVERRIDE={
                "AU": None,
                "NZ": {"numeric": None},
                "US": {"numeric": 900},
            }
        ):
            self.assertEqual(countries.numeric("AU"), None)
            self.assertEqual(countries.numeric("NZ"), None)
            self.assertEqual(countries.numeric("US"), 900)

    def test_alpha2_override_new(self):
        with self.settings(COUNTRIES_OVERRIDE={"XX": "Neverland"}):
            self.assertEqual(countries.alpha2("XX"), "XX")

    def test_ioc_code(self):
        self.assertEqual(countries.ioc_code("BS"), "BAH")

    def test_ioc_code_override(self):
        with self.settings(
            COUNTRIES_OVERRIDE={
                "BS": "Bahamas in Pajamas",
                "AU": None,
                "NZ": {"ioc_code": ""},
                "XX": "Neverland",
                "US": {"ioc_code": "XXX"},
                "XK": {"name": "Kosovo", "ioc_code": "KOS"},
            }
        ):
            self.assertEqual(
                countries.ioc_code("BS"),
                "BAH",
                "Should still use built-in code if only name changed",
            )
            self.assertEqual(
                countries.ioc_code("AU"),
                "",
                "Should be empty since country was marked not present",
            )
            self.assertEqual(
                countries.ioc_code("NZ"),
                "",
                "Should be empty since country exists but IOC code cleared",
            )
            self.assertEqual(
                countries.ioc_code("XX"),
                "",
                "Should be empty for a custom country with no IOC code",
            )
            self.assertEqual(
                countries.ioc_code("US"), "XXX", "Should use provided custom IOC code"
            )
            self.assertEqual(
                countries.ioc_code("XK"),
                "KOS",
                "Should use IOC code for a custom country that provides a code",
            )

    def test_fetch_by_name(self):
        code = countries.by_name("Brunei")
        self.assertEqual(code, "BN")

    def test_fetch_by_name_official(self):
        code = countries.by_name("brunei darussalam")
        self.assertEqual(code, "BN")

    def test_fetch_by_name_case_insensitive(self):
        code = countries.by_name("bRuNeI")
        self.assertEqual(code, "BN")

    def test_fetch_by_name_old(self):
        code = countries.by_name("Czech Republic")
        self.assertEqual(code, "CZ")

    def test_fetch_by_name_old_case_insensitive(self):
        code = countries.by_name("Czech republic")
        self.assertEqual(code, "CZ")

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_fetch_by_name_i18n(self):
        code = countries.by_name("Estados Unidos", language="es")
        self.assertEqual(code, "US")

    def test_fetch_by_name_no_match(self):
        self.assertEqual(countries.by_name("Neverland"), "")

    def test_fetch_by_name_custom(self):
        with self.settings(
            COUNTRIES_ONLY={
                "AU": {"name": "Oz"},
                "NZ": {"names": ["New Zealand", "Hobbiton"]},
            }
        ):
            self.assertEqual(countries.by_name("Oz"), "AU")
            self.assertEqual(countries.by_name("New Zealand"), "NZ")
            self.assertEqual(countries.by_name("Hobbiton"), "NZ")

    def test_fetch_by_name_regex(self):
        codes = countries.by_name(r"([ao])\1", regex=True)
        # Cook Islands, Cameroon, Sint Maarten
        self.assertEqual(set(codes), {"CK", "CM", "SX"})

    def test_multiple_labels(self):
        with self.settings(
            COUNTRIES_ONLY={
                "NZ": {"names": ["New Zealand", "Hobbiton"]},
                "AU": {"name": "Oz"},
                "NV": "Neverland",
            }
        ):
            list_countries = list(countries)
        self.assertEqual(
            list_countries,
            [
                ("NZ", "Hobbiton"),
                ("NV", "Neverland"),
                ("NZ", "New Zealand"),
                ("AU", "Oz"),
            ],
        )


class CountriesFirstTest(BaseTest):
    def test_countries_first(self):
        with self.settings(COUNTRIES_FIRST=["NZ", "AU"]):
            self.assertEqual(
                list(countries)[:5],
                [("NZ", "New Zealand"), ("AU", "Australia")] + FIRST_THREE_COUNTRIES,
            )

    def test_countries_first_break(self):
        with self.settings(
            COUNTRIES_FIRST=["NZ", "AU"], COUNTRIES_FIRST_BREAK="------"
        ):
            self.assertEqual(
                list(countries)[:6],
                [("NZ", "New Zealand"), ("AU", "Australia"), ("", "------")]
                + FIRST_THREE_COUNTRIES,
            )

    def test_countries_first_some_valid(self):
        with self.settings(
            COUNTRIES_FIRST=["XX", "NZ", "AU"], COUNTRIES_FIRST_BREAK="------"
        ):
            countries_list = list(countries)
        self.assertEqual(
            countries_list[:6],
            [("NZ", "New Zealand"), ("AU", "Australia"), ("", "------")]
            + FIRST_THREE_COUNTRIES,
        )
        self.assertEqual(len(countries_list), EXPECTED_COUNTRY_COUNT + 1)

    def test_countries_first_no_valid(self):
        with self.settings(COUNTRIES_FIRST=["XX"], COUNTRIES_FIRST_BREAK="------"):
            countries_list = list(countries)
        self.assertEqual(countries_list[:3], FIRST_THREE_COUNTRIES)
        self.assertEqual(len(countries_list), EXPECTED_COUNTRY_COUNT)

    def test_countries_first_repeat(self):
        with self.settings(COUNTRIES_FIRST=["NZ", "AU"], COUNTRIES_FIRST_REPEAT=True):
            countries_list = list(countries)
        self.assertEqual(len(countries_list), EXPECTED_COUNTRY_COUNT + 2)
        sorted_codes = [item[0] for item in countries_list[2:]]
        sorted_codes.index("NZ")
        sorted_codes.index("AU")

    def test_countries_first_len(self):
        with self.settings(COUNTRIES_FIRST=["NZ", "AU", "XX"]):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT + 2)

    def test_countries_first_break_len(self):
        with self.settings(
            COUNTRIES_FIRST=["NZ", "AU", "XX"], COUNTRIES_FIRST_BREAK="------"
        ):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT + 3)

    def test_countries_first_break_len_no_valid(self):
        with self.settings(COUNTRIES_FIRST=["XX"], COUNTRIES_FIRST_BREAK="------"):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT)

    def test_sorted_countries_first_english(self):
        with self.settings(
            COUNTRIES_FIRST=["NZ", "CA", "YE"], COUNTRIES_FIRST_SORT=True
        ):
            countries_list = list(countries)
            sorted_codes = [item[0] for item in countries_list[:3]]
            # Canada, New Zealand, Yemen
            self.assertEqual(["CA", "NZ", "YE"], sorted_codes)

    def test_unsorted_countries_first_english(self):
        with self.settings(
            COUNTRIES_FIRST=["NZ", "CA", "YE"], COUNTRIES_FIRST_SORT=False
        ):
            countries_list = list(countries)
            unsorted_codes = [item[0] for item in countries_list[:3]]
            self.assertEqual(["NZ", "CA", "YE"], unsorted_codes)

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_sorted_countries_first_translated(self):
        with self.settings(
            COUNTRIES_FIRST=["NZ", "CA", "YE"], COUNTRIES_FIRST_SORT=True
        ):
            lang = translation.get_language()
            translation.activate("eo")
            try:
                countries_list = list(countries)
                sorted_codes = [item[0] for item in countries_list[:3]]
                # Jemeno, Kanado, Nov-Zelando
                self.assertEqual(["YE", "CA", "NZ"], sorted_codes)
            finally:
                translation.activate(lang)

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_translation_fallback_from_common_name(self):
        trans_fall_countries = custom_countries.TranslationFallbackCountries()
        lang = translation.get_language()
        try:
            translation.activate("eo")
            self.assertEqual(trans_fall_countries.name("NZ"), "Nov-Zelando")
            translation.activate("en@test")
            self.assertEqual(trans_fall_countries.name("NZ"), "Endor")
        finally:
            translation.activate(lang)

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_translation_fallback_from_old_name(self):
        trans_fall_countries = custom_countries.TranslationFallbackCountries()

        lang = translation.get_language()
        try:
            translation.activate("eo")
            self.assertEqual(trans_fall_countries.name("NZ"), "Nov-Zelando")
            translation.activate("en@test")
            self.assertEqual(trans_fall_countries.name("NZ"), "Endor")
        finally:
            translation.activate(lang)

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_translation_fallback_override(self):
        lang = translation.get_language()

        try:
            translation.activate("eo")
            self.assertEqual(countries.name("NZ"), "Nov-Zelando")
            translation.activate("en@test")
            self.assertEqual(countries.name("NZ"), "New Zealand")

            # Avoid this translation with makemessages
            gtl = translation.gettext_lazy
            with self.settings(COUNTRIES_OVERRIDE={"NZ": gtl("Middle Earth")}):
                del countries.countries
                self.assertEqual(countries.name("NZ"), "Endor")
        finally:
            translation.activate(lang)

    @pytest.mark.skipif(not settings.USE_I18N, reason="No i18n")
    def test_translation_fallback_override_names(self):
        # Avoid this translation with makemessages
        gtl = translation.gettext_lazy
        with self.settings(
            COUNTRIES_OVERRIDE={
                "NZ": {
                    "names": [
                        gtl("Middle Earth"),
                        translation.gettext_lazy("New Zealand"),
                    ]
                }
            }
        ):

            lang = translation.get_language()
            try:
                translation.activate("eo")
                self.assertEqual(countries.name("NZ"), "Nov-Zelando")
                translation.activate("en@test")
                self.assertEqual(countries.name("NZ"), "Endor")
            finally:
                translation.activate(lang)

    def test_first_multiple_labels(self):
        with self.settings(
            COUNTRIES_FIRST=["NZ"],
            COUNTRIES_FIRST_BREAK="------",
            COUNTRIES_ONLY={
                "NZ": {"names": ["New Zealand", "Hobbiton"]},
                "NV": "Neverland",
            },
        ):
            countries_list = list(countries)
        self.assertEqual(
            countries_list,
            [
                ("NZ", "New Zealand"),
                ("", "------"),
                ("NZ", "Hobbiton"),
                ("NV", "Neverland"),
            ],
        )


class TestCountriesCustom(BaseTest):
    def test_countries_limit(self):
        fantasy_countries = custom_countries.FantasyCountries()
        self.assertEqual(
            list(fantasy_countries), [("NV", "Neverland"), ("NZ", "New Zealand")]
        )
        self.assertEqual(len(fantasy_countries), 2)
