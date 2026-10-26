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
        Anklet graphs on subsets of `nodes` which are reduced
        (i.e. unchanged by :meth:`AnkletGraph.reduce`), connected and planar.
    """

    # Fix an order for the non-trivial anklets
    anklets = [a for a in anklets_on(nodes, subsets=True) if len(a) > 1]

    # Record which pairs of anklets taken together as hyperedges give a reduced planar anklet graph
    compatible = {i: set[int]() for i in range(len(anklets))}
    for (i, a), (j, b) in combinations_with_replacement(enumerate(anklets), 2):
        g = AnkletGraph[T]()
        g.add_hyperedges_from([a, b])
        g.reduce()
        if g.number_of_hyperedges() == 2 and g.is_planar():
            compatible[i].add(j)

    # Init queue with single-hyperedge anklet graphs
    queue = []
    for i, a in enumerate(anklets):
        g = AnkletGraph[T](indices=(i,))
        g.add_hyperedge(a)
        queue.append(g)

    # Add single-node anklet graphs to list of connected graphs
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
    """Return all balloon graphs on the given nodes.

    Parameters
    ----------
    nodes : Collection[T]
        Set of nodes.

    Returns
    -------
    list[BalloonGraph[T]]
        Balloon graphs on with node set `nodes`

    Examples
    --------
    >>> [len(balloon_graphs_on(range(n))) for n in range(5)]
    [1, 1, 3, 20, 361]
    """
    # Store indices into the array with the anklet graphs themselves
    anklet_graphs = anklet_graphs_on(nodes)
    for i, ag in enumerate(anklet_graphs):
        ag.attributes['index'] = i

    queue = [BalloonGraph[T]()]
    balloon_graphs: list[BalloonGraph[T]] = []
    while queue:
        bg = queue.pop(0)

        # Iterate over anklet graphs with index larger than those already present
        # that share at most one node with 'bg'
        i_start = 0 if not bg else max(g.attributes['index'] for g in bg) + 1
        for ag in anklet_graphs[i_start:]:
            if len(ag.nodes & bg.nodes) <= 1:
                # Assign balloon attribute to the new component - up to one past the current largest
                b_max = 0 if not bg else max(g.attributes['balloon'] for g in bg) + 1
                for b in range(b_max + 1):
                    bg_new = BalloonGraph(*(g.copy() for g in bg), ag.copy())
                    bg_new[-1].attributes['balloon'] = b
                    try:
                        bg_new.check_structure()
                        queue.append(bg_new)
                    except ValueError:
                        pass

        # Add to list of balloon graphs to return if all nodes are present
        if bg.nodes == set(nodes):
            for ag in bg:
                ag.attributes.pop('index')
            balloon_graphs.append(bg)

    return balloon_graphs
