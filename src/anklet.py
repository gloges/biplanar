"""Combinatorial anklets."""

from collections.abc import Hashable
from typing import Self


class Anklet[T: Hashable](tuple[T, ...]):
    """An anklet is a combinatorial bracelet with all beads distinct."""

    def __new__(cls, *beads: T) -> Self:
        if len(set(beads)) != len(beads):
            raise ValueError("beads are not distinct")
        return super().__new__(cls, beads)

    @classmethod
    def from_iterable(cls, values: Iterable[T] = (), /) -> Self:
        return cls(*values)

    def __repr__(self) -> str:
        return "ank(" + ", ".join(repr(bead) for bead in self) + ")"

    def __add__(self, value: object) -> NotImplementedType:
        return NotImplemented

    def __mul__(self, value: object) -> NotImplementedType:
        return NotImplemented

    def __rmul__(self, value: object) -> NotImplementedType:
        return NotImplemented

