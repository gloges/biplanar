"""Combinatorial anklets."""

from collections.abc import Hashable
from typing import Self


class Anklet[T: Hashable](tuple[T, ...]):
    """An anklet is a combinatorial bracelet with all beads distinct."""

    def __new__(cls, *beads: T) -> Self:
        if len(set(beads)) != len(beads):
            raise ValueError("beads are not distinct")
        return super().__new__(cls, beads)
