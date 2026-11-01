"""Zipping of anklet graphs."""

from collections.abc import Hashable
from itertools import product
from .anklet import Anklet
from .anklet_graph import AnkletGraph
from .union import disjoint_union, union


def splice[T](a: Anklet[T], b: Anklet[T]) -> set[Anklet[T]]:
    """Splice together two anklets on distinct beads.

    Splicing together `a` and `b` amounts to cutting the anklets apart into linear sequences
    of beads whose ends are then joined up to form one larger anklet. This process involves a choice
    of where to cut each anklet and a choice of relative orientation before being joined together.

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

    See Also
    --------
    :meth:`pinched_splice`

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
    >>> splice(Anklet(0, 1, 2), Anklet(2, 3, 4))
    Traceback (most recent call last):
    ...
    ValueError: the two anklets have the beads {2} in common
    """
    if set(a) & set(b):
        raise ValueError(f"the two anklets have the beads {set(a) & set(b)} in common")
    return {
        Anklet.from_iterable(rep_a + rep_b)
        for rep_a in a.representatives()
        for rep_b in b.representatives()
    }


def pinched_splice[T](a: Anklet[T], b: Anklet[T]) -> set[tuple[Anklet[T], Anklet[T]]]:
    """Splice together two anklets with one bead in common into a pair of anklets.

    Pairs of anklets are formed by the following process:
    - Consider the two anklets as cyclic graphs and take their union. Since they have one bead
    in common this produces a "figure-eight" graph.
    - Cut open each of the anklet cycles at an edge, resulting in a starlike graph with exactly
    four dangling "half-edges".
    - Join up the "half-edges" in pairs so that each is with a new partner. The produces again
    a "figure-eight" graph.
    - Split apart the figure-eight graph at the hub node into two anklets with one bead in common.

    The above steps involve choices for where to make the cuts and how to glue the loose ends
    back together. If `a` and `b` have `m` and `n` beads, respectively, then at most `2(m + n)`
    pairs of anklets are returned.

    Parameters
    ----------
    a, b : Anklet[T]
        Two anklets sharing exactly one bead.

    Returns
    -------
    set[tuple[Anklet[T], Anklet[T]]]
        All pairs of anklets which result from splicing together `a` and `b`, as described above.

    Raises
    ------
    ValueError
        If `a` and `b` do not have exactly one bead in common.

    See Also
    --------
    :meth:`splice`

    Examples
    --------
    >>> pinched_splice(Anklet(0, 1), Anklet(0))
    {(A(0, 1), A(0))}
    >>> pinched_splice(Anklet(0, 1, 2), Anklet(0))
    {(A(0, 1), A(0, 2)), (A(0, 1, 2), A(0))}
    >>> pinched_splice(Anklet(0, 1), Anklet(0, 2))
    {(A(0, 1), A(0, 2)), (A(0, 1, 2), A(0))}
    >>> for a_pair in sorted(pinched_splice(Anklet(0, 1), Anklet(0, 2, 3))):
    ...     print(a_pair)
    (A(0, 1), A(0, 2, 3))
    (A(0, 1, 2), A(0, 3))
    (A(0, 1, 3), A(0, 2))
    (A(0, 1, 3, 2), A(0))
    (A(0, 1, 2, 3), A(0))
    >>> pinched_splice(Anklet(0, 1, 2), Anklet(1, 2, 3))
    Traceback (most recent call last):
    ...
    ValueError: the two anklets do not have exactly one bead in common: {1, 2}
    """
    common_beads = set(a) & set(b)
    if len(common_beads) != 1:
        raise ValueError(f"the two anklets do not have exactly one bead in common: {common_beads}")
    common_bead = common_beads.pop()

    anklet_pairs = set()
    for rep_a, rep_b in product(a.representatives(), b.representatives()):
        seq = rep_a + rep_b
        i1 = seq.index(common_bead)
        i2 = seq.index(common_bead, i1 + 1)
        anklet_1 = Anklet.from_iterable(seq[i1:i2])
        anklet_2 = Anklet.from_iterable(seq[i2:] + seq[:i1])
        if (anklet_1, anklet_2) not in anklet_pairs and (anklet_2, anklet_1) not in anklet_pairs:
            anklet_pairs.add((anklet_1, anklet_2))
    return anklet_pairs


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
        raise ValueError(f"the two anklet graphs have the nodes {g.nodes & h.nodes} in common")
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


def pinched_zipper[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> list[AnkletGraph[T]]:

    common_nodes = g.nodes & h.nodes
    if len(common_nodes) != 1:
        raise ValueError(
            f"the two anklet graphs do not have exactly one node in common: {common_nodes}"
        )
    if not g.is_connected():
        raise ValueError("'g' is not connected")
    if not h.is_connected():
        raise ValueError("'h' is not connected")

    common_node = common_nodes.pop()
    hypes_g = [hype_g for hype_g, _ in g.hyperedges if common_node in hype_g]
    hypes_h = [hype_h for hype_h, _ in h.hyperedges if common_node in hype_h]

    anklet_graphs = []
    for hype_g, hype_h in product(hypes_g, hypes_h):
        for hypes_spliced in pinched_splice(hype_g, hype_h):
            anklet_graph = union(g, h)
            anklet_graph.remove_hyperedge(hype_g)
            anklet_graph.remove_hyperedge(hype_h)
            anklet_graph.add_hyperedges_from(hypes_spliced)
            anklet_graphs.append(anklet_graph)

    return anklet_graphs
