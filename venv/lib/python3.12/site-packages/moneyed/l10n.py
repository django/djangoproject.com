from __future__ import annotations

from typing import TYPE_CHECKING

from babel.numbers import LC_NUMERIC
from babel.numbers import format_currency as babel_format_currency

if TYPE_CHECKING:
    from .classes import Money


def format_money(
    money: Money,
    format: str | None = None,
    locale: str = LC_NUMERIC,
    currency_digits: bool = True,
    format_type: str = "standard",
    decimal_quantization: bool = True,
) -> str:
    """
    See https://babel.pocoo.org/en/latest/api/numbers.html
    """
    return babel_format_currency(  # type: ignore[no-any-return]
        money.amount,
        money.currency.code,
        format=format,
        locale=locale,
        currency_digits=currency_digits,
        format_type=format_type,
        decimal_quantization=decimal_quantization,
    )
