from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

A = TypeVar("A")
R = TypeVar("R")


class cached_property(Generic[A, R]):
    """
    Decorator that creates converts a method with a single
    self argument into a property cached on the instance.
    """

    def __init__(self, func: Callable[[A], R]) -> None:
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, instance: A, type: type) -> R:
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res
