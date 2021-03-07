from __future__ import annotations

from functools import reduce
from typing import Generic, TypeVar, Callable, List

T = TypeVar('T')
V = TypeVar('V')
W = TypeVar('W')


class Option(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def map(self, f: Callable[..., V], *args) -> Option:
        if self.value is not None:
            return Option(f(self.value, *args))
        else:
            return self

    def get(self, default=None):
        return self.value if self.value is not None else default


def add(*args):
    return sum(args)


def mul(*args):
    return reduce(lambda x, y: x*y, args)
