"""Zipping of anklet graphs."""

from collections.abc import Hashable
from itertools import product
from .anklet import Anklet
from .anklet_graph import AnkletGraph
from .union import disjoint_union


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
    """Return the anklet graphs which result from zipping together two connected anklet graphs.

    Zipping together `g` and `h` amounts to taking their disjoint union and then picking a pair
    of hyperedges, one from `g` and one from `h`, and replacing them by their various splicings.

    If either `g` or `h` has only a single node and no hyperedges then a single 1-node hyperedge
    is temporarily added before picking pairs of hyperedges to splice.

    Parameters
    ----------
    g, h : AnkletGraph[T]
        Two connected anklet graphs on disjoint sets of nodes.

    Returns
    -------
    list[AnkletGraph[T]]
        The anklet graphs which result from zipping together `g` and `h`.

    Raises
    ------
    ValueError
        If `g` and `h` have nodes in common or if either is not connected.

    Examples
    --------
    >>> from inflated_graphs import Anklet
    >>> g = AnkletGraph(hyperedges=[Anklet(0, 1)])
    >>> h = AnkletGraph(hyperedges=[Anklet(2, 3)])
    >>> for agraph in zipper_disjoint(g, h):
    ...     print(agraph.data_string())
    <0, 1, 2, 3 | A(0, 1, 2, 3)>
    <0, 1, 2, 3 | A(0, 1, 3, 2)>
    >>> g = AnkletGraph(hyperedges=[Anklet(0, 1)])
    >>> h = AnkletGraph(hyperedges=[Anklet(2, 3), Anklet(3, 4, 5)])
    >>> for agraph in zipper_disjoint(g, h):
    ...     print(agraph.data_string())
    <0, 1, 2, 3, 4, 5 | A(3, 4, 5) + A(0, 1, 2, 3)>
    <0, 1, 2, 3, 4, 5 | A(3, 4, 5) + A(0, 1, 3, 2)>
    <0, 1, 2, 3, 4, 5 | A(2, 3) + A(0, 1, 4, 5, 3)>
    <0, 1, 2, 3, 4, 5 | A(2, 3) + A(0, 1, 5, 3, 4)>
    <0, 1, 2, 3, 4, 5 | A(2, 3) + A(0, 1, 4, 3, 5)>
    <0, 1, 2, 3, 4, 5 | A(2, 3) + A(0, 1, 5, 4, 3)>
    <0, 1, 2, 3, 4, 5 | A(2, 3) + A(0, 1, 3, 5, 4)>
    <0, 1, 2, 3, 4, 5 | A(2, 3) + A(0, 1, 3, 4, 5)>
    """
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
