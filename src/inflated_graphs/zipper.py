"""Zipping of anklet graphs."""

from .anklet import Anklet


def splice[T](a: Anklet[T], b: Anklet[T]) -> set[Anklet[T]]:
    """Splice together two anklets on distinct beads in all possible ways.

    Splicing together `a` and `b` amounts to cutting the anklets apart into tuples
    which are then joined end-to-end with a choice of relative orientation into a larger anklet.

    Parameters
    ----------
    a, b : Anklet[T]
        Two anklets with no beads in common.

    Returns
    -------
    set[Anklet[T]]
        Set of anklets resulting from splicing together `a` and `b`.

    Raises
    ------
    ValueError
        If `a` and `b` have beads in common.

    Examples
    --------
    >>> splice(Anklet(0), Anklet(1))
    {A(0, 1)}
    >>> splice(Anklet(0), Anklet(1, 2))
    {A(0, 1, 2)}
    >>> splice(Anklet(0, 1), Anklet(2, 3))
    {A(0, 1, 2, 3), A(0, 1, 3, 2)}
    >>> splice(Anklet(0), Anklet(1, 2, 3))
    {A(0, 1, 2, 3), A(0, 2, 3, 1), A(0, 3, 1, 2)}
    """
    if set(a) & set(b):
        raise ValueError(f"a and b have the beads {set(a) & set(b)} in common")
    return {
        Anklet.from_iterable(rep_a + rep_b)
        for rep_a in a.representatives()
        for rep_b in b.representatives()
    }
