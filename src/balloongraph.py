"""Balloon graphs."""

from collections.abc import Hashable
from typing import Self
import networkx as nx
from ankletgraph import AnkletGraph


class BalloonGraph[T: Hashable](tuple[AnkletGraph[T], ...]):
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str
    _valid_structure_hash: int

    def __new__(cls, *ankletgraphs: AnkletGraph[T], name: str = "") -> Self:
        bg = super().__new__(cls, ankletgraphs)
        bg._name = name
        bg._valid_structure_hash = 0
        return bg

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

    def get_data_string(self) -> str:
        """Return a string encoding of the balloon graph's data.

        The balloon attribute and two data strings of each anklet graph are formated
        as `"[{ballon} | {node_data} | {hyperedge_data}]"` and then joined via `", "`.

        Returns
        -------
        str
            String encoding of the data needed to reconstruct the balloon graph.

        Raises
        ------
        ValueError
            If the balloon graph does not have a valid structure.

        Examples
        --------
        >>> from anklet import Anklet
        >>> ag1 = AnkletGraph(range(0, 4), balloon='a')
        >>> ag2 = AnkletGraph(range(4, 7), balloon='b')
        >>> ag1.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2, 3): 2})
        >>> ag2.add_hyperedge(Anklet(4, 5), 3)
        >>> bg = BalloonGraph(ag1, ag2)
        >>> bg.get_data_string()
        '[a | 0, 1, 2, 3 | A(0, 1) + 2 × A(1, 2, 3)], [b | 4, 5, 6 | 3 × A(4, 5)]'
        """
        return ", ".join(
            '[' + " | ".join([str(g.get_attribute('balloon')), *g.get_data_strings()]) + ']'
            for g in self
        )

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return set.union(*[g.nodes for g in self])

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def check_structure(self) -> None:
        """Validate the structure of the balloon graph.

        Two conditions must be met for the structure of the balloon graph to be considered valid:
        - The component anklet graphs have 'balloon' attributes which are equal
        for components which share a node.
        - The *incidence* graph, with nodes both the nodes and components of the balloon graph
        and with edges between "node" nodes and "component" nodes when that component contains
        that node, is acyclic (i.e. a forest graph).

        Returns quietly if the structure is valid.

        Raises
        ------
        ValueError
            If (i) an component anklet graph does not have a 'balloon' attribute,
            (ii) two components with a node in common have different values for their 'balloon'
            attributes or (iii) the node-component incidence graph described above is not a forest.
        """
        if hash(g.get_data_strings() for g in self) == self._valid_structure_hash:
            # If the hash has not changed since the last successful structure check,
            # there is no need to check again
            return

        g = nx.Graph()
        for i, component in enumerate(self):
            try:
                component.get_attribute('balloon')
            except KeyError as exc:
                self._valid_structure_hash = 0
                raise ValueError(
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
                self._valid_structure_hash = 0
                raise ValueError(
                    f"the anklet graphs containing node {n} (indices: {nbr_indices})"
                    " do not all have the same values for their 'balloon' attribute"
                )

        if not nx.is_forest(g):
            cycle_data = [
                f"(node {n})" if 'node' in g.nodes[n] else f"(component {n[1]})"
                for n, _ in nx.find_cycle(g)
            ]
            self._valid_structure_hash = 0
            raise ValueError(
                "Invalid structure. the node-component incidence graph contains the cycle\n" +
                " → ".join([*cycle_data, cycle_data[0]])
            )

        # The structure is valid:
        # save the hash to avoid checking the structure again if it doesn't change
        self._valid_structure_hash = hash(g.get_data_strings() for g in self)
