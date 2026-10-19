"""Balloon graphs."""

from collections.abc import Hashable
import networkx as nx
from ankletgraph import AnkletGraph


class BalloonGraph[T: Hashable](list[AnkletGraph[T]]):
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str

    def __init__(self, *, name: str = "") -> None:
        self._name = name

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Meta
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def name(self) -> str:
        """The name of the graph."""
        return self._name

    @name.setter
    def name(self, s: str) -> None:
        self._name = s

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def check_structure(self) -> None:
        """Validate the structure of the balloon graph.

        Two conditions must be met for the structure of a balloon graph to be considered valid:
        - The component anklet graphs have 'balloon' attributes which are equal
        for components which share a node.
        - The *incidence* graph with nodes both the nodes and components of the balloon graph
        and with edges between "node" nodes and "component" nodes when that component contains
        that node is acyclic (i.e. a forest graph).

        Returns quietly if the structure is valid.

        Raises
        ------
        KeyError
            If an component anklet graph does not have a 'balloon' attribute.
        ValueError
            If two components with a node in common have different values
            for their 'balloon' attributes or if the incidence graph is not a forest.
        """

        g = nx.Graph()
        for i, component in enumerate(self):
            try:
                component.get_attribute('balloon')
            except KeyError as exc:
                raise KeyError(
                    f"the anklet graph at index {i} does not have a 'balloon' attribute"
                ) from exc

            component_node = ("component", i)
            g.add_node(component_node, component=True)
            for n in component:
                g.add_node(n, node=True)
                g.add_edge(n, component_node)

        for n in nx.get_node_attributes(g, 'node'):
            nbr_indices = [nbr[1] for nbr in g.neighbors(n)]
            if len({self[i].get_attribute('balloon') for i in nbr_indices}) != 1:
                raise ValueError(
                    f"the anklet graphs containing node {n} (indices: {nbr_indices})"
                    " do not all have the same values for their 'balloon' attribute"
                )

        if not nx.is_forest(g):
            cycle_data = [
                f"(node {n})" if 'node' in g.nodes[n] else f"(component {n[1]})"
                for n, _ in nx.find_cycle(g)
            ]
            raise ValueError(
                "Invalid structure. Meta-graph contains the cycle\n" +
                " → ".join([*cycle_data, cycle_data[0]])
            )
