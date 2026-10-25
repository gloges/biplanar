"""Unions of anklet graphs."""

from collections.abc import Hashable, Iterable
from .anklet_graph import AnkletGraph


def union_all[T: Hashable](graphs: Iterable[AnkletGraph[T]]) -> AnkletGraph[T]:
    """Return the union of a collection of anklet graphs.

    The union for nodes the union of the nodes of the individual anklet graphs and for its multiset
    of hyperedges the union of the hyperedge multisets of the individual anklet graphs.

    Parameters
    ----------
    graphs : Iterable[AnkletGraph[T]]
        A sequence of anklet graphs.

    Returns
    -------
    AnkletGraph[T]
        The union of the anklet graphs.
    """
    graph_union = AnkletGraph[T]()
    for g in graphs:
        graph_union.add_nodes_from(g)
        graph_union.add_hyperedges_from(dict(g.hyperedges))
    return graph_union


def union[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> AnkletGraph[T]:
    """Return the union of two anklet graphs.

    The union of `g` and `h` has for nodes the union of the nodes of `g` and `h`
    and for its multiset of hyperedges the union of the hyperedge multisets of `g` and `h`.

    Parameters
    ----------
    g, h : AnkletGraph[T]
        Two anklet graphs.

    Returns
    -------
    AnkletGraph[T]
        The union of `g` and `h`.

    Examples
    --------
    >>> g = AnkletGraph.from_data_strings("0, 1, 2", "A(0, 1, 2) + 2 × A(1, 2)", int)
    >>> h = AnkletGraph.from_data_strings("1, 2, 3, 4, 5", "A(1, 2) + A(1, 3, 4)", int)
    >>> gh = union(g, h)
    >>> gh.nodes
    {0, 1, 2, 3, 4, 5}
    >>> gh.hyperedges
    ((A(0, 1, 2), 1), (A(1, 2), 3), (A(1, 3, 4), 1))
    """
    return union_all([g, h])


def disjoint_union_all[T: Hashable](graphs: Iterable[AnkletGraph[T]]) -> AnkletGraph[T]:
    """Return the union of a collection of anklet graphs on disjoint sets of nodes.

    Parameters
    ----------
    graphs : Iterable[AnkletGraph[T]]
        A sequence of anklet graphs with pairwise no nodes in common.

    Returns
    -------
    AnkletGraph[T]
        The union of the anklet graphs.

    Raises
    ------
    ValueError
        If any two graphs have nodes in common.
    """
    if len(set().union(g.nodes for g in graphs)) != sum(g.number_of_nodes() for g in graphs):
        raise ValueError("two or more anklet graphs have node(s) in common")
    return union_all(graphs)


def disjoint_union[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> AnkletGraph[T]:
    """Return the union of two anklet graphs on disjoint sets of nodes.

    Parameters
    ----------
    g, h : AnkletGraph[T]
        Two anklet graphs with no nodes in common.

    Returns
    -------
    AnkletGraph[T]
        The union of `g` and `h`.

    Raises
    ------
    ValueError
        If `g` and `h` have nodes in common.

    Examples
    --------
    >>> g = AnkletGraph.from_data_strings("0, 1, 2", "A(0, 1, 2) + 2 × A(1, 2)", int)
    >>> h = AnkletGraph.from_data_strings("3, 4, 5", "A(3, 4)", int)
    >>> gh = disjoint_union(g, h)
    >>> gh.nodes
    {0, 1, 2, 3, 4, 5}
    >>> gh.hyperedges
    ((A(0, 1, 2), 1), (A(1, 2), 2), (A(3, 4), 1))
    >>> g = AnkletGraph.from_data_strings("0, 1, 2", "A(0, 1, 2) + 2 × A(1, 2)", int)
    >>> h = AnkletGraph.from_data_strings("1, 2, 3, 4, 5", "A(1, 2) + A(1, 3, 4)", int)
    >>> disjoint_union(g, h)
    Traceback (most recent call last):
    ...
    ValueError: the two anklet graphs share the node(s) {1, 2}
    """
    if g.nodes & h.nodes:
        raise ValueError(f"the two anklet graphs share the node(s) {g.nodes & h.nodes}")
    return union(g, h)
