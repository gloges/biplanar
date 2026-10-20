"""Balloon graphs."""

from collections.abc import Hashable, Mapping
from typing import Any, Self
import networkx as nx
from ankletgraph import AnkletGraph


class BalloonGraph[T: Hashable](tuple[AnkletGraph[T], ...]):
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str
    _attr: dict[str, Any]
    _valid_structure_hash: int | None

    def __new__(cls, *ankletgraphs: AnkletGraph[T], name: str = "", **attr: Any) -> Self:
        bg = super().__new__(cls, ankletgraphs)
        bg._name = name
        bg._attr = attr
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

    @property
    def attributes(self) -> dict[str, Any]:
        """The balloon graph's mutable attribute dictionary.

        Changes to the returned dictionary modify this graphs's attributes.
        Assigning a mapping replaces the dictionary with a shallow copy of that mapping.
        """
        return self._attr

    @attributes.setter
    def attributes(self, value: Mapping[str, Any]) -> None:
        self._attr = dict(value)

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
            '[' + " | ".join([str(ag.get_attribute('balloon')), *ag.get_data_strings()]) + ']'
            for ag in self
        )

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return set().union(*[ag.nodes for ag in self])

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Reduction
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def reduce(self) -> None:
        """Reduce each component anklet graph: see :meth:`AnkletGraph.reduce`."""
        for ag in self:
            ag.reduce()

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
        do not all have the same value for their 'balloon' attribute
        >>> g2.set_attributes(balloon='a')
        >>> BalloonGraph(g1, g2).check_structure()
        >>> g2.add_hyperedge(Anklet(1, 2))
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: Invalid structure. the node-component incidence graph contains the cycle
        (graph 0) → (node 1) → (graph 1) → (node 2) → (graph 0)
        """
        if self._get_check_structure_hash() == self._valid_structure_hash:
            # If the hash has not changed since the last successful structure check,
            # there is no need to check again
            return

        # Check the basic structure of individual components. Each component anklet graph...
        for i, ag in enumerate(self):
            # 1) is non-empty
            if not ag.nodes:
                self._reset_valid_structure_hash()
                raise ValueError(f"the anklet graph at index {i} is empty")

            # 2) is planar
            if not ag.is_planar():
                self._reset_valid_structure_hash()
                raise ValueError(f"the anklet graph at index {i} is not planar")

            # 3) has a 'balloon' attribute
            try:
                ag.get_attribute('balloon')
            except KeyError as exc:
                self._reset_valid_structure_hash()
                raise ValueError(
                    f"the anklet graph at index {i} does not have a 'balloon' attribute"
                ) from exc

        # Check structure of the incidence graph:
        inc_graph = self.to_incidence_graph()

        # 1) If a component anklet graph has a single node then that node
        #    is not contained in any other component.
        for i, ag in enumerate(self):
            if len(ag.nodes) == 1:
                # The node 'n' of 'g' corresponds to the unique node of 'ag'. It should only have
                # one neighbor in the incidence graph, namely node 'i' (corresponding to 'ag')
                n = list(inc_graph.adj[i])[0]
                if set(inc_graph.adj[n]) != {i}:
                    self._reset_valid_structure_hash()
                    raise ValueError(
                        f"the anklet graph at index {i} has only one node {ag.nodes}"
                        f"\nand this node appears in multiple components: {inc_graph.adj[n]}"
                    )

        # 2) For each node the components containing it must all have the same value for 'balloon'.
        for i in inc_graph:
            if 'node' in inc_graph.nodes[i]:
                if len({self[j].get_attribute('balloon') for j in inc_graph.neighbors(i)}) != 1:
                    self._reset_valid_structure_hash()
                    raise ValueError(
                        f"the anklet graphs containing node {inc_graph.nodes[i]['node']}"
                        f" (indices: {sorted(inc_graph.neighbors(i))})\n"
                        "do not all have the same value for their 'balloon' attribute"
                    )

        # 3) There are no cycles.
        if not nx.is_forest(inc_graph):
            cycle_data = [
                f"(node {inc_graph.nodes[i]['node']})"
                if 'node' in inc_graph.nodes[i]
                else f"(graph {i})"
                for i, _ in nx.find_cycle(inc_graph)
            ]
            self._reset_valid_structure_hash()
            raise ValueError(
                "Invalid structure. the node-component incidence graph contains the cycle\n" +
                " → ".join([*cycle_data, cycle_data[0]])
            )

        # The structure is valid:
        # save the hash to avoid checking the structure again if it doesn't change
        self._valid_structure_hash = self._get_check_structure_hash()
