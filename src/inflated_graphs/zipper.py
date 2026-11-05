"""Zipping of anklet graphs."""

from collections.abc import Hashable
from itertools import product
from .anklet import Anklet
from .anklet_graph import AnkletGraph
from .union import union


def pinched_splice[T](a: Anklet[T], b: Anklet[T]) -> set[tuple[Anklet[T], Anklet[T]]]:
    """Splice together two anklets with exactly one bead in common.

    Each anklet must have at least two beads.

    Pairs of anklets are formed by the following process:
    - For both `a` and `b` pick a bead *other* than the bead they have in common.
    - Viewing the anklet `a` as a labeled polygon, cut in a straight line from its chosen bead
    to the common bead; the polygon falls into two pieces, each with both the chosen
    and common beads.
    - Similarly for `b`.
    - Join up the polygon pieces in pairs, one from `a` with one from `b`, such that the raw cut
    edges meet with the common bead vertices together.
    - Reinterpret the newly formed labeled polygons as anklets.

    The above steps produce pairs of anklets which have exactly three beads in common (the bead
    common to `a` and `b` and the two chosen beads). There are several choices involved: where
    to make the cuts and how to glue the pieces back together.
    If `a` and `b` have `m ≥ 3` and `n ≥ 3` beads, respectively, then this splicing process produces
    `2(m - 1)(n - 1)` pairs of anklets. For `m = 2` this number is halved and similarly for `n = 2`.

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
        If `a` and `b` do not have exactly one bead in common or if either has only one bead.

    See Also
    --------
    :meth:`pinched_zipper`

    Examples
    -------- 
    >>> pinched_splice(Anklet(0, 1), Anklet(0, 2))
    {(A(0, 1, 2), A(0, 2, 1))}
    >>> pinched_splice(Anklet(0, 1), Anklet(0, 2, 3))
    {(A(0, 1, 3), A(0, 2, 3, 1)), (A(0, 1, 2, 3), A(0, 2, 1))}
    >>> for a_pair in sorted(pinched_splice(Anklet(0, 1, 2), Anklet(0, 3, 4))):
    ...     print(a_pair)
    (A(0, 1, 4), A(0, 3, 4, 1, 2))
    (A(0, 1, 3, 4), A(0, 3, 1, 2))
    (A(0, 1, 2, 4), A(0, 3, 4, 2))
    (A(0, 1, 3), A(0, 4, 3, 1, 2))
    (A(0, 1, 4, 3), A(0, 4, 1, 2))
    (A(0, 1, 2, 3), A(0, 4, 3, 2))
    (A(0, 1, 2, 4, 3), A(0, 4, 2))
    (A(0, 1, 2, 3, 4), A(0, 3, 2))
    >>> pinched_splice(Anklet(0, 1, 2), Anklet(1, 2, 3))
    Traceback (most recent call last):
    ...
    ValueError: the two anklets do not have exactly one bead in common: {1, 2}
    >>> pinched_splice(Anklet(0, 1, 2), Anklet(2))
    Traceback (most recent call last):
    ...
    ValueError: b = A(2) has only one bead
    """
    common_beads = set(a) & set(b)
    if len(common_beads) != 1:
        raise ValueError(f"the two anklets do not have exactly one bead in common: {common_beads}")
    common_bead = common_beads.pop()

    if len(a) == 1:
        raise ValueError(f"a = {a} has only one bead")
    if len(b) == 1:
        raise ValueError(f"b = {b} has only one bead")

    pairs = set()
    for rep_a, rep_b in product(a.representatives(), b.representatives()):
        if common_bead not in (rep_a[0], rep_b[0]):
            i_a = rep_a.index(common_bead)
            i_b = rep_b.index(common_bead)
            anklet_1 = Anklet.from_iterable(rep_a[i_a:] + rep_a[:1] + rep_b[:i_b])
            anklet_2 = Anklet.from_iterable(rep_b[i_b:] + rep_b[:1] + rep_a[:i_a])
            if (anklet_1, anklet_2) not in pairs and (anklet_2, anklet_1) not in pairs:
                pairs.add((anklet_1, anklet_2))
    return pairs


def pinched_zipper[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> list[AnkletGraph[T]]:
    """Return the anklet graphs which result from zipping together two anklet graphs.

    The anklet graphs `g` and `h` must have exactly one node in common: call it `n₀`.
    Both `g` and `h` must have at least one hyperedge containing `n₀` but neither may have
    the hyperedge `A(n₀)`.

    Pinch-zipping together `g` and `h` amounts to taking their union and then picking a pair
    of hyperedges, one from `g` and one from `h`, containing `n` and replacing them by their
    pinched splicings (see :meth:`pinched_splice`).

    Parameters
    ----------
    g, h : AnkletGraph[T]
        Two anklet graphs sharing exactly one node.

    Returns
    -------
    list[AnkletGraph[T]]
        The anklet graphs which result from zipping together `g` and `h` as described above.

    Raises
    ------
    ValueError
        If `g` and `h` do not have exactly one node in common, if either contains a length-one
        hyperedge with the common node or if either does not contain any hyperedges with
        the common node.

    See Also
    --------
    :meth:`pinched_splice`

    Examples
    --------
    >>> from inflated_graphs import Anklet
    >>> g = AnkletGraph(hyperedges=[Anklet(0, 1), Anklet(0, 2)])
    >>> h = AnkletGraph(hyperedges=[Anklet(0, 3), Anklet(3, 4)])
    >>> for ag in pinched_zipper(g, h):
    ...     print(ag.data_string())
    <0, 1, 2, 3, 4 | A(0, 2) + A(3, 4) + 2 × A(0, 1, 3)>
    <0, 1, 2, 3, 4 | A(0, 1) + A(3, 4) + 2 × A(0, 2, 3)>
    >>> g = AnkletGraph(hyperedges=[Anklet(0, 1, 2), Anklet(1, 2, 3)])
    >>> h = AnkletGraph(hyperedges=[Anklet(0, 4, 5), Anklet(4, 5, 6)])
    >>> for ag in pinched_zipper(g, h):
    ...     print(ag.data_string())
    <0, 1, 2, 3, 4, 5, 6 | A(0, 1, 4) + A(1, 2, 3) + A(4, 5, 6) + A(0, 2, 1, 4, 5)>
    <0, 1, 2, 3, 4, 5, 6 | A(1, 2, 3) + A(4, 5, 6) + A(0, 1, 2, 4) + A(0, 2, 4, 5)>
    <0, 1, 2, 3, 4, 5, 6 | A(0, 2, 4) + A(1, 2, 3) + A(4, 5, 6) + A(0, 1, 2, 4, 5)>
    <0, 1, 2, 3, 4, 5, 6 | A(1, 2, 3) + A(4, 5, 6) + A(0, 1, 4, 5) + A(0, 2, 1, 4)>
    <0, 1, 2, 3, 4, 5, 6 | A(1, 2, 3) + A(4, 5, 6) + A(0, 1, 2, 5) + A(0, 2, 5, 4)>
    <0, 1, 2, 3, 4, 5, 6 | A(0, 2, 5) + A(1, 2, 3) + A(4, 5, 6) + A(0, 1, 2, 5, 4)>
    <0, 1, 2, 3, 4, 5, 6 | A(0, 1, 5) + A(1, 2, 3) + A(4, 5, 6) + A(0, 2, 1, 5, 4)>
    <0, 1, 2, 3, 4, 5, 6 | A(1, 2, 3) + A(4, 5, 6) + A(0, 1, 5, 4) + A(0, 2, 1, 5)>
    """
    common_nodes = g.nodes & h.nodes
    if len(common_nodes) != 1:
        raise ValueError(
            f"the two anklet graphs do not have exactly one node in common: {common_nodes}"
        )
    common_node = common_nodes.pop()

    hypes_g = [hype_g for hype_g, _ in g.hyperedges if common_node in hype_g]
    hypes_h = [hype_h for hype_h, _ in h.hyperedges if common_node in hype_h]

    if Anklet(common_node) in hypes_g:
        raise ValueError(f"'g' has the hyperedge {Anklet(common_node)}")
    if Anklet(common_node) in hypes_h:
        raise ValueError(f"'h' has the hyperedge {Anklet(common_node)}")
    if not hypes_g:
        raise ValueError(f"'g' has no hyperedges containing {common_node}")
    if not hypes_h:
        raise ValueError(f"'h' has no hyperedges containing {common_node}")

    anklet_graphs = []
    for hype_g, hype_h in product(hypes_g, hypes_h):
        for hypes_spliced in pinched_splice(hype_g, hype_h):
            anklet_graph = union(g, h)
            anklet_graph.remove_hyperedge(hype_g)
            anklet_graph.remove_hyperedge(hype_h)
            anklet_graph.add_hyperedges_from(hypes_spliced)
            anklet_graphs.append(anklet_graph)

    return anklet_graphs
