"""Methods for generating anklets, anklet graphs and balloon graphs."""

from collections.abc import Collection, Hashable, Iterable
from itertools import chain, combinations, combinations_with_replacement, permutations
from .anklet import Anklet
from .anklet_graph import AnkletGraph
from .balloon_graph import BalloonGraph


def powerset[T](iterable: Iterable[T]) -> chain[tuple[T, ...]]:
    """Subsequences of the iterable from shortest to longest.

    See https://docs.python.org/3/library/itertools.html#recipes.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def anklets_on[T](beads: Collection[T], *, subsets: bool = False) -> set[Anklet[T]]:
    """Return anklets on a set of beads.

    If `subsets` is `False`, returns all anklets which contain *all* of the beads.
    For `n ≥ 1` beads the number of such anklets is the order of the alternating group `Aₙ₋₁`,
    OEIS sequence [A001710](https://oeis.org/A001710).

    If `subsets` is `True`, returns all anklets which contain any *subset* of the beads.
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
    >>> list(anklets_on(range(4)))
    [A(0, 1, 2, 3), A(0, 1, 3, 2), A(0, 2, 1, 3)]
    >>> sorted(anklets_on(range(3), subsets=True), key=lambda x: (len(x), tuple(x)))
    [A(), A(0), A(1), A(2), A(0, 1), A(0, 2), A(1, 2), A(0, 1, 2)]
    >>> [len(anklets_on(range(n))) for n in range(8)]  # A001710
    [1, 1, 1, 1, 3, 12, 60, 360]
    >>> [len(anklets_on(range(n), subsets=True)) for n in range(8)]  # A116723
    [1, 2, 4, 8, 18, 53, 219, 1201]
    """
    if subsets:
        return set.union(*[anklets_on(bead_subset) for bead_subset in powerset(beads)])
    return {Anklet.from_iterable(bead_perm) for bead_perm in permutations(beads)}


def anklet_graphs_on[T: Hashable](nodes: Collection[T]) -> list[AnkletGraph[T]]:
    """Return all reduced, connected, planar anklet graphs on subsets of `nodes`.

    Parameters
    ----------
    nodes : Collection[T]
        Nodes for the anklet graphs.

    Returns
    -------
    list[AnkletGraph[T]]
        Anklet graphs on non-empty subsets of `nodes` which are reduced, connected and planar.

    Examples
    --------
    >>> [len(anklet_graphs_on(range(n))) for n in range(5)]
    [0, 1, 3, 12, 189]
    >>> for ag in anklet_graphs_on(range(2)):
    ...     print("nodes = {:7} hyperedges = {}".format(*ag.get_data_strings()))
    nodes = 0       hyperedges = 
    nodes = 1       hyperedges = 
    nodes = 0, 1    hyperedges = A(0, 1)
    >>> for ag in anklet_graphs_on(range(3)):
    ...     print("nodes = {:10} hyperedges = {}".format(*ag.get_data_strings()))
    nodes = 0          hyperedges = 
    nodes = 1          hyperedges = 
    nodes = 2          hyperedges = 
    nodes = 1, 2       hyperedges = A(1, 2)
    nodes = 0, 1, 2    hyperedges = A(0, 1, 2)
    nodes = 0, 1       hyperedges = A(0, 1)
    nodes = 0, 2       hyperedges = A(0, 2)
    nodes = 0, 1, 2    hyperedges = A(0, 1) + A(1, 2)
    nodes = 0, 1, 2    hyperedges = A(0, 2) + A(1, 2)
    nodes = 0, 1, 2    hyperedges = 2 × A(0, 1, 2)
    nodes = 0, 1, 2    hyperedges = A(0, 1) + A(0, 2)
    nodes = 0, 1, 2    hyperedges = A(0, 1) + A(0, 2) + A(1, 2)
    """

    # Fix an order for the non-trivial anklets
    anklets = [a for a in anklets_on(nodes, subsets=True) if len(a) > 1]

    # Record which pairs of anklets taken together as hyperedges give a reduced planar anklet graph
    compatible = {i: set[int]() for i in range(len(anklets))}
    for (i, a), (j, b) in combinations_with_replacement(enumerate(anklets), 2):
        g = AnkletGraph(hyperedges=[a, b])
        g.reduce()
        if g.number_of_hyperedges() == 2 and g.is_planar():
            compatible[i].add(j)

    # Init queue with single-hyperedge anklet graphs
    queue = [AnkletGraph(hyperedges=[a], indices=(i,)) for i, a in enumerate(anklets)]

    # Add single-node anklet graphs to list of reduced, connected, planar anklet graphs
    # (but not to the queue to have edges added)
    anklet_graphs = [AnkletGraph([n]) for n in nodes]

    while queue:
        g = queue.pop(0)

        # Only need to consider adding new hyperedges which are pairwise
        # compatible with the pre-existing hyperedges of 'g'
        g_indices = g.attributes['indices']
        for i_new in set.intersection(*[compatible[i] for i in g_indices]):
            g_new = g.copy()
            g_new.add_hyperedge(anklets[i_new])
            if g_new.is_planar():
                g_new.attributes['indices'] = (*g_indices, i_new)
                queue.append(g_new)

        if g.is_connected():
            g.attributes.clear()
            anklet_graphs.append(g)

    return anklet_graphs


def balloon_graphs_on[T: Hashable](nodes: Collection[T]) -> list[BalloonGraph[T]]:
    """Return all reduced balloon graphs on the given nodes.

    Parameters
    ----------
    nodes : Collection[T]
        Nodes for the balloon graphs.

    Returns
    -------
    list[BalloonGraph[T]]
        Balloon graphs with node set `nodes`

    Examples
    --------
    >>> [len(balloon_graphs_on(range(n))) for n in range(5)]
    [1, 1, 3, 20, 361]
    >>> for g in balloon_graphs_on(range(2)):
    ...     print(g.get_data_string())
    [<0, 1 | A(0, 1)>]
    [<0 | >, <1 | >]
    [<0 | >], [<1 | >]
    >>> for g in balloon_graphs_on(range(3)):
    ...     print(g.get_data_string())
    [<0, 1, 2 | A(0, 1, 2)>]
    [<0, 1, 2 | A(0, 1) + A(1, 2)>]
    [<0, 1, 2 | A(0, 2) + A(1, 2)>]
    [<0, 1, 2 | 2 × A(0, 1, 2)>]
    [<0, 1, 2 | A(0, 1) + A(0, 2)>]
    [<0, 1, 2 | A(0, 1) + A(0, 2) + A(1, 2)>]
    [<0 | >, <1, 2 | A(1, 2)>]
    [<0 | >], [<1, 2 | A(1, 2)>]
    [<1 | >, <0, 2 | A(0, 2)>]
    [<1 | >], [<0, 2 | A(0, 2)>]
    [<2 | >, <0, 1 | A(0, 1)>]
    [<2 | >], [<0, 1 | A(0, 1)>]
    [<1, 2 | A(1, 2)>, <0, 1 | A(0, 1)>]
    [<1, 2 | A(1, 2)>, <0, 2 | A(0, 2)>]
    [<0, 1 | A(0, 1)>, <0, 2 | A(0, 2)>]
    [<0 | >, <1 | >, <2 | >]
    [<0 | >, <1 | >], [<2 | >]
    [<0 | >, <2 | >], [<1 | >]
    [<0 | >], [<1 | >, <2 | >]
    [<0 | >], [<1 | >], [<2 | >]
    """
    # Store indices into the array with the anklet graphs themselves
    anklet_graphs = anklet_graphs_on(nodes)
    for i, ag in enumerate(anklet_graphs):
        ag.attributes['index'] = i

    queue = [BalloonGraph[T]()]
    balloon_graphs: list[BalloonGraph[T]] = []
    while queue:
        bgraph = queue.pop(0)

        # Iterate over anklet graphs with index larger than those already present
        # that share at most one node with 'bg'
        index_start = 0
        if bgraph:
            index_start = max(ag.attributes['index'] for balloon in bgraph for ag in balloon) + 1
        for ag_new in anklet_graphs[index_start:]:
            common_nodes = ag_new.nodes & bgraph.nodes
            if not common_nodes:
                # Can add 'ag_new' to any pre-existing balloons or start a new one
                for i in range(len(bgraph)):
                    bgraph_new = bgraph.copy()
                    bgraph_new[i].append(ag_new.copy())
                    queue.append(bgraph_new)
                bgraph_new = bgraph.copy()
                bgraph_new.append([ag_new.copy()])
                queue.append(bgraph_new)
            elif len(common_nodes) == 1:
                # Identify the balloon of bgraph which has the node in common with ag_new
                common_node = list(common_nodes)[0]
                i = [common_node in bnodes for bnodes in bgraph.balloon_nodes()].index(True)
                if all(ag.nodes != {common_node} for ag in bgraph[i]):
                    bgraph_new = bgraph.copy()
                    bgraph_new[i].append(ag_new.copy())
                    queue.append(bgraph_new)

        # Add to list of balloon graphs to return if all nodes are present
        if bgraph.nodes == set(nodes):
            for balloon in bgraph:
                for ag in balloon:
                    ag.attributes.pop('index')
            balloon_graphs.append(bgraph)

    return balloon_graphs
