"""Zipping of anklet graphs."""

from collections.abc import Hashable
from itertools import product
from .anklet import Anklet
from .anklet_graph import AnkletGraph
from .anklet_graph_unions import disjoint_union


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


def zipper_disjoint[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> list[AnkletGraph[T]]:
    if g.nodes & h.nodes:
        raise ValueError(f"'g' and 'h' have the nodes {g.nodes & h.nodes} in common")
    if not g.is_connected():
        raise ValueError("'g' is not connected")
    if not h.is_connected():
        raise ValueError("'h' is not connected")

    # Edge cases where g or h is empty
    if not g:
        return [h.copy()]
    if not h:
        return [g.copy()]

    # If either g or h has just a single node then we will need at least one hyperedge "A(n)" below
    g_added_hype = g.number_of_hyperedges() == 0
    h_added_hype = h.number_of_hyperedges() == 0
    if g_added_hype:
        g.add_hyperedge(Anklet.from_iterable(g))
    if h_added_hype:
        h.add_hyperedge(Anklet.from_iterable(h))

    anklet_graphs = []
    for (hype_g, _), (hype_h, _) in product(g.hyperedges, h.hyperedges):
        for hype_spliced in splice(hype_g, hype_h):
            anklet_graph = disjoint_union(g, h)
            anklet_graph.remove_hyperedge(hype_g)
            anklet_graph.remove_hyperedge(hype_h)
            anklet_graph.add_hyperedge(hype_spliced)
            anklet_graphs.append(anklet_graph)

    # Remove the added 1-node hyperedge
    if g_added_hype:
        g.remove_hyperedge(Anklet.from_iterable(g))
    if h_added_hype:
        h.remove_hyperedge(Anklet.from_iterable(h))

    return anklet_graphs
