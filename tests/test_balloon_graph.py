"""Tests for BalloonGraph."""

from itertools import product
import networkx as nx
import pytest
from inflated_graphs.generate import balloon_graphs_on


# n = 4 takes ~1 min
@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_balloon_graph_partial_order(n: int) -> None:
    """Check properties of the partial order for balloon graphs on `n` nodes.

    Confirms that the relation `g ≤ h` satisfies the transitive property, namely that `g₁ ≤ g₂`
    and `g₂ ≤ g₃` imply `g₁ ≤ g₃`, and that the directed graph of comparisons is acyclic.

    Parameters
    ----------
    n : int
        Number of nodes.

    Raises
    ------
    AssertionError
        If the transitivity property fails or if the directed graph of comparisons contains a cycle.
    """
    graphs = balloon_graphs_on(range(n))

    poset_graph = nx.DiGraph()
    for (i, g), (j, h) in product(enumerate(graphs), repeat=2):
        if i != j and g <= h:
            poset_graph.add_edge(i, j)

    for i, j in poset_graph.out_edges:
        for _, k in poset_graph.out_edges(j):
            assert poset_graph.has_edge(i, k)

    assert nx.is_directed_acyclic_graph(poset_graph)
