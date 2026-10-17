"""Methods for generating anklets and anklet graphs."""

from collections.abc import Collection, Iterable
from itertools import chain, combinations, permutations
from anklet import Anklet


def powerset[T](iterable: Iterable[T]) -> chain[tuple[T, ...]]:
    """Subsequences of the iterable from shortest to longest.

    See https://docs.python.org/3/library/itertools.html#recipes.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def get_anklets[T](beads: Collection[T], *, subsets: bool = False) -> set[Anklet[T]]:
    if subsets:
        return set.union(*[get_anklets(bead_subset) for bead_subset in powerset(beads)])
    return {Anklet.from_iterable(bead_perm) for bead_perm in permutations(beads)}
