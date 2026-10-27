"""Unions of anklet graphs."""

from collections.abc import Collection, Hashable
from .anklet_graph import AnkletGraph


def union_all[T: Hashable](graphs: Collection[AnkletGraph[T]]) -> AnkletGraph[T]:
    """Return the union of a collection of anklet graphs.

    The returned anklet graph has for its nodes and hyperedge multiset
    the union of the nodes and hyperedge multisets over the individual anklet graphs.

    The attributes of the union are updated in iterating over `graphs`;
    attributes of later anklet graphs overwrite those of earlier anklet graphs.

    Parameters
    ----------
    graphs : Collection[AnkletGraph[T]]
        A collection of anklet graphs.

    Returns
    -------
    AnkletGraph[T]
        The union of the anklet graphs.

    See Also
    --------
    :meth:`union`,
    :meth:`disjoint_union_all`,
    :meth:`disjoint_union`
    """
    graph_union = AnkletGraph[T]()
    for g in graphs:
        graph_union.add_nodes_from(g)
        graph_union.add_hyperedges_from(dict(g.hyperedges))
        graph_union.attributes.update(g.attributes)
    return graph_union


def union[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> AnkletGraph[T]:
    """Return the union of two anklet graphs.

    The returned anklet graph has for its nodes and hyperedge multiset
    the union of the nodes and hyperedge multisets over `g` and `h`.

    The attributes of the union are a combination of those of `g` and `h`. If `g` and `h` both
    have the same attribute then the value of that attribute for `h` takes precidence.

    Parameters
    ----------
    g, h : AnkletGraph[T]
        Two anklet graphs.

    Returns
    -------
    AnkletGraph[T]
        The union of `g` and `h`.

    See Also
    --------
    :meth:`union_all`,
    :meth:`disjoint_union_all`,
    :meth:`disjoint_union`

    Examples
    --------
    >>> from inflated_graphs import Anklet
    >>> g = AnkletGraph(hyperedges={Anklet(0, 1, 2): 1, Anklet(1, 2): 2})
    >>> h = AnkletGraph([1, 2, 3, 4, 5], {Anklet(1, 2): 1, Anklet(1, 3, 4): 2})
    >>> gh = union(g, h)
    >>> gh.nodes
    {0, 1, 2, 3, 4, 5}
    >>> gh.hyperedges
    ((A(0, 1, 2), 1), (A(1, 2), 3), (A(1, 3, 4), 2))
    """
    return union_all([g, h])


def disjoint_union_all[T: Hashable](graphs: Collection[AnkletGraph[T]]) -> AnkletGraph[T]:
    """Return the union of a collection of anklet graphs on disjoint sets of nodes.

    Parameters
    ----------
    graphs : Collection[AnkletGraph[T]]
        A collection of anklet graphs on different sets of nodes.

    Returns
    -------
    AnkletGraph[T]
        The union of the anklet graphs.

    Raises
    ------
    ValueError
        If any two graphs have nodes in common.

    See Also
    --------
    :meth:`union_all`,
    :meth:`union`,
    :meth:`disjoint_union`
    """
    if len(set().union(g.nodes for g in graphs)) != sum(g.number_of_nodes() for g in graphs):
        raise ValueError("two or more anklet graphs have node(s) in common")
    return union_all(graphs)


def disjoint_union[T: Hashable](g: AnkletGraph[T], h: AnkletGraph[T]) -> AnkletGraph[T]:
    """Return the union of two anklet graphs on disjoint sets of nodes.

    Parameters
    ----------
    g, h : AnkletGraph[T]
        Two anklet graphs on different sets of nodes.

    Returns
    -------
    AnkletGraph[T]
        The union of `g` and `h`.

    Raises
    ------
    ValueError
        If `g` and `h` have nodes in common.

    See Also
    --------
    :meth:`union_all`,
    :meth:`union`,
    :meth:`disjoint_union_all`

    Examples
    --------
    >>> from inflated_graphs import Anklet
    >>> g = AnkletGraph(hyperedges={Anklet(0, 1, 2): 1, Anklet(1, 2): 2})
    >>> h = AnkletGraph({3, 4, 5}, [Anklet(3, 4)])
    >>> gh = disjoint_union(g, h)
    >>> gh.nodes
    {0, 1, 2, 3, 4, 5}
    >>> gh.hyperedges
    ((A(0, 1, 2), 1), (A(1, 2), 2), (A(3, 4), 1))
    >>> h.add_hyperedge(Anklet(1, 2, 3))
    >>> disjoint_union(g, h)
    Traceback (most recent call last):
    ...
    ValueError: the two anklet graphs share the node(s) {1, 2}
    """
    if g.nodes & h.nodes:
        raise ValueError(f"the two anklet graphs share the node(s) {g.nodes & h.nodes}")
    return union(g, h)
