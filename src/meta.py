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
    """Return anklets on a set of beads.

    If `subsets` is `False`, returns all anklets which contain all of the beads.
    For `n ≥ 1` beads the number of such anklets is the order of the alternating group `Aₙ₋₁`,
    OEIS sequence [A001710](https://oeis.org/A001710).

    If `subsets` is `True`, returns all anklets which contain any subset of the beads.
    The number of such anklets is given by OEIS sequence [A116723](https://oeis.org/A116723).

    Parameters
    ----------
    beads : Collection[T]
        Set of beads.
    subsets : bool, optional (default=False)
        Whether to allow subsets of the beads.

    Returns
    -------
    set[Anklet[T]]
        Set of unique anklets.

    Examples
    --------
    >>> list(get_anklets(range(4)))
    [A(0, 1, 2, 3), A(0, 1, 3, 2), A(0, 2, 1, 3)]
    >>> sorted(get_anklets(range(3), subsets=True), key=lambda x: (len(x), tuple(x)))
    [A(), A(0), A(1), A(2), A(0, 1), A(0, 2), A(1, 2), A(0, 1, 2)]
    >>> [len(get_anklets(range(n))) for n in range(8)]
    [1, 1, 1, 1, 3, 12, 60, 360]
    >>> [len(get_anklets(range(n), subsets=True)) for n in range(8)]
    [1, 2, 4, 8, 18, 53, 219, 1201]
    """
    if subsets:
        return set.union(*[get_anklets(bead_subset) for bead_subset in powerset(beads)])
    return {Anklet.from_iterable(bead_perm) for bead_perm in permutations(beads)}
