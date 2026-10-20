"""Balloon graphs."""

from collections.abc import Hashable
from typing import Self
import networkx as nx
from ankletgraph import AnkletGraph


class BalloonGraph[T: Hashable](tuple[AnkletGraph[T], ...]):
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str
    _valid_structure_hash: int | None

    def __new__(cls, *ankletgraphs: AnkletGraph[T], name: str = "") -> Self:
        bg = super().__new__(cls, ankletgraphs)
        bg._name = name
        bg._reset_valid_structure_hash()
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
        return set().union(*[g.nodes for g in self])

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Incidence
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def incidence(self) -> dict[T, set[int]]:
        """Return the incidence data.

        Returns
        -------
        dict[T, set[int]]
            Dictionary keyed by nodes.
            Values are the sets of indices for the anklet graph components containing that node.

        See Also
        --------
        :meth:`to_incidence_graph`
        """
        inc = {n: set() for n in self.nodes}
        for i, ag in enumerate(self):
            for n in ag.nodes:
                inc[n].add(i)
        return inc

    def to_incidence_graph(self) -> nx.Graph:
        """Return the simple graph reflecting node-component incidences in the balloon graph.

        The returned graph has the *nodes* and *components* of the balloon graph for nodes and edges
        between "node" nodes and "component" nodes when a node belongs to a component anklet graph:
        this is a simple, bipartite graph.

        All nodes in the bipartite graph are integers: "node" nodes have an attribute with name
        'node' which stores the balloon graph nodes. Nodes without a 'node' attribute are
        "component" nodes and are simply the integer index into the balloon graph.

        Returns
        -------
        networkx.Graph
            A simple, bipartite graph on the nodes and component anklet graphs of the balloon graph.

        See Also
        --------
        :meth:`incidence`
        """

        # Add integer nodes to the graph:
        # - For component-nodes use the indices of the component anklet graphs
        # - For node-node just use the next 'n' integers (store the correspondence in 'node_ids')
        g = nx.Graph()
        g.add_nodes_from(range(len(self)))
        node_ids = {n: len(self) + i for i, n in enumerate(self.nodes)}
        g.add_nodes_from((i, {'node': n}) for n, i in node_ids.items())

        # Add edges between component-nodes and node-nodes when one contains the other
        for i, ag in enumerate(self):
            for n in ag:
                g.add_edge(i, node_ids[n])

        return g

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _get_check_structure_hash(self) -> int:
        return hash(ag.get_data_strings() for ag in self)

    def _reset_valid_structure_hash(self) -> None:
        self._valid_structure_hash = None

    def check_structure(self) -> None:
        """Validate the structure of the balloon graph.

        Several conditions must be met for the structure of a balloon graph to be considered valid:
        - All components must be non-empty and planar.
        - If a component has a single node then that node does not appear in any other component.
        - The component anklet graphs have 'balloon' attributes which are equal
        for components which share a node.
        - The *incidence* graph, with nodes both the nodes and components of the balloon graph
        and with edges between "node" nodes and "component" nodes when that component contains
        that node, is acyclic (i.e. a forest graph).

        Returns quietly if the structure is valid.

        Raises
        ------
        ValueError
            If any of the above conditions are not met (a short message explains the issue).

        Examples
        --------
        >>> from anklet import Anklet
        >>> g1 = AnkletGraph(balloon='a')
        >>> g1.add_hyperedge(Anklet(0, 1, 2))
        >>> g2 = AnkletGraph()
        >>> g2.add_hyperedge(Anklet(2, 3, 4))
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graph at index 1 does not have a 'balloon' attribute
        >>> g2.set_attributes(balloon='b')
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graphs containing node 2 (indices: [0, 1])
        do not all have the same values for their 'balloon' attribute
        >>> g2.set_attributes(balloon='a')
        >>> BalloonGraph(g1, g2).check_structure()
        >>> g2.add_hyperedge(Anklet(1, 2))
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: Invalid structure. the node-component incidence graph contains the cycle
        (component 0) → (node 1) → (component 1) → (node 2) → (component 0)
        """
        if self._get_check_structure_hash() == self._valid_structure_hash:
            # If the hash has not changed since the last successful structure check,
            # there is no need to check again
            return

        g = nx.Graph()
        for i, component in enumerate(self):
            if not component:
                raise ValueError(f"the anklet graph at index {i} is empty")
            if len(component) == 1:
                for j, comp2 in enumerate(self):
                    if i != j and component.nodes <= comp2.nodes:
                        raise ValueError(
                            f"the anklet graph at index {i} has only one node {component.nodes}"
                            f"\nand this node also appears in the graph at index {j}"
                        )
            if not component.is_planar():
                raise ValueError(f"the anklet graph at index {i} is not planar")

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
                    "\ndo not all have the same values for their 'balloon' attribute"
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
        self._valid_structure_hash = self._get_check_structure_hash()
