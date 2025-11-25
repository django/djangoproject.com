from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional, Union, overload, type_check_only

from django.db.models.expressions import CombinedExpression, F
from django.utils.safestring import SafeText

from typing_extensions import Literal, TypedDict

from moneyed import Currency, Money as _DefaultMoney

__all__ = ["Money", "Currency"]
DefaultMoney = _DefaultMoney

@type_check_only
class _FormatOptions(TypedDict):
    "Format options parameter."
    format: Optional[str]
    locale: str
    currency_digits: bool
    format_type: Literal["standard", "standard:short", "name"]
    decimal_quantization: bool

class Money(DefaultMoney):
    use_l10n: Any
    decimal_places: Any
    format_options: Any

    def __init__(self, *args, format_options: Optional[_FormatOptions] = ..., **kwargs) -> None: ...
    @overload  # type: ignore[override]
    def __add__(self, other: Money) -> Money: ...
    @overload
    def __add__(self, other: F) -> CombinedExpression: ...
    @overload  # type: ignore[override]
    def __sub__(self, other: Money) -> Money: ...
    @overload
    def __sub__(self, other: F) -> CombinedExpression: ...
    @overload  # type: ignore[override]
    def __mul__(self, other: _NumericalType) -> Money: ...
    @overload
    def __mul__(self, other: F) -> CombinedExpression: ...
    @overload  # type: ignore[override]
    def __truediv__(self, other: _NumericalType) -> Money: ...
    @overload
    def __truediv__(self, other: F) -> CombinedExpression: ...
    def __rtruediv__(self, other) -> None: ...  # type: ignore[override]
    @property
    def is_localized(self) -> bool: ...
    def __html__(self) -> SafeText: ...
    def __round__(self, n: Any | None = ...) -> Money: ...
    def round(self, ndigits: int = ...) -> Money: ...  # type: ignore[override]
    def __pos__(self) -> Money: ...
    def __neg__(self) -> Money: ...
    def __abs__(self) -> Money: ...
    def __rmod__(self, other) -> Money: ...
    def __radd__(self, other) -> Money: ...  # type: ignore[override]
    def __rmul__(self, other) -> Money: ...  # type: ignore[override]

def get_current_locale() -> str: ...

_NumericalType = Union[Decimal, float, int]
