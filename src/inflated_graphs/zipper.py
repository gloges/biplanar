"""Zipping of anklet graphs."""

from .anklet import Anklet


def splice[T](a: Anklet[T], b: Anklet[T]) -> set[Anklet[T]]:
    if set(a) & set(b):
        raise ValueError(f"a and b have the beads {set(a) & set(b)} in common")
    return {
        Anklet.from_iterable(rep_a + rep_b)
        for rep_a in a.representatives()
        for rep_b in b.representatives()
    }
