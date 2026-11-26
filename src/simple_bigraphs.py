"""Methods for generating simple (path) bi-graphs."""

from itertools import product
import networkx as nx
from padded_graphs import Anklet, AnkletGraph, BalloonGraph, BiGraph


def planar_complement_planar(n_max: int, remove_complementary: bool) -> list[list[nx.Graph]]:
    """Return all planar graphs on at most `n_max` nodes for which the complement is also planar.

    The returned graphs are organized by number of nodes.

    References
    ----------
    [oeis.org/A391132](https://oeis.org/A391132)

    Examples
    --------
    >>> [len(graphs_n) for graphs_n in planar_complement_planar(6, False)]
    [1, 1, 2, 4, 11, 32, 128]
    >>> [len(graphs_n) for graphs_n in planar_complement_planar(6, True)]
    [1, 1, 1, 2, 6, 17, 64]
    """
    if n_max <= 0:
        raise ValueError(f"n_max = {n_max} is not a positive integer")

    graphs = [[nx.Graph()], [nx.complete_graph(1)]]
    for n in range(1, n_max):
        graphs.append([])
        for g in graphs[n]:
            for which_in_g in product([True, False], repeat=n):
                g_new = g.copy()
                g_new.add_node(n)
                for i, add_to_g in enumerate(which_in_g):
                    if add_to_g:
                        g_new.add_edge(i, n)
                h_new = nx.complement(g_new)
                if nx.is_planar(g_new) and nx.is_planar(h_new):
                    if not any(
                        nx.is_isomorphic(g_new, g2)
                        or (remove_complementary and nx.is_isomorphic(h_new, g2))
                        for g2 in graphs[n+1]
                    ):
                        graphs[n+1].append(g_new)
    return graphs


def simple_complete_bigraphs(n_max: int = 8) -> list[list[BiGraph[int]]]:
    """Return all simple, complete bi-graphs on at most `n_max` nodes.

    The returned bi-graphs are organized by number of nodes. The bi-graphs on `n` nodes are simple
    in the sense that each balloon has at most one anklet graph and has only 2-hyperedges,
    and they are complete in the sense that they contain all `ₙC₂` edges between pairs of nodes.

    Examples
    --------
    >>> [len(graphs_n) for graphs_n in simple_complete_bigraphs(6)]
    [1, 1, 1, 2, 6, 17, 64]
    """
    bigraphs = []
    for graphs_n in planar_complement_planar(n_max, True):
        bigraphs.append([])
        for g in graphs_n:
            h = nx.complement(g)
            # There is a separate balloon (with a single anklet graph) for each connected component
            ags_g = [AnkletGraph[int](nodes=cc) for cc in nx.connected_components(g)]
            ags_h = [AnkletGraph[int](nodes=cc) for cc in nx.connected_components(h)]
            for edge in g.edges:
                for ag in ags_g:
                    if set(edge) <= ag.nodes:
                        ag.add_hyperedge(Anklet.from_iterable(edge))
            for edge in h.edges:
                for ag in ags_h:
                    if set(edge) <= ag.nodes:
                        ag.add_hyperedge(Anklet.from_iterable(edge))
            big = BiGraph(
                BalloonGraph(*[[ag] for ag in ags_g]),
                BalloonGraph(*[[ag] for ag in ags_h])
            )
            big.check_structure()
            bigraphs[-1].append(big)

    return bigraphs
