"""Balloon graphs."""

from collections.abc import Callable, Hashable, Mapping
from typing import Any, Self
import networkx as nx
from .anklet_graph import AnkletGraph
from .anklet_graph_unions import disjoint_union as anklet_graph_disjoint_union


class BalloonGraph[T: Hashable](list[AnkletGraph[T]]):
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str
    _attr: dict[str, Any]
    _valid_structure: int | None

    def __init__(self, *anklet_graphs: AnkletGraph[T], name: str = "", **attr: Any) -> None:
        super().__init__(anklet_graphs)
        self._name = name
        self._attr = attr
        self._reset_valid_structure()

    @classmethod
    def from_data_string(
        cls,
        data: str,
        balloon_interpreter: Callable[[str], Any],
        node_interpreter: Callable[[str], T]
    ) -> Self:
        """Construct a balloon graph from a string encoding of its anklet graphs.

        The input string must follow the format produced by :meth:`BalloonGraph.get_data_string`.

        Parameters
        ----------
        data : str
            String representation of the anklet graphs.
        balloon_interpreter : Callable[[str], Ant]
            A function that converts a balloon's string representation into the desired type.
        node_interpreter : Callable[[str], T]
            A function that converts a node's string representation into a node of type `T`.

        Returns
        -------
        Self
            A balloon graph.

        Raises
        ------
        ValueError
            If there is a parsing error (a short message explains the issue).

        Examples
        --------
        A typical use case:

        >>> g = BalloonGraph.from_data_string(
        ...     "[a | 0, 1, 2 | 3 × A(0, 1) + A(1, 2)], [a | 2, 3 | A(2, 3)]", str, int
        ... )
        >>> for ag in g:
        ...    print(ag.attributes['balloon'], str(ag.nodes).ljust(9), ag.hyperedges)
        a {0, 1, 2} ((A(0, 1), 3), (A(1, 2), 1))
        a {2, 3}    ((A(2, 3), 1),)

        The data for each anklet graph must include a balloon attribute, nodes and hyperedges:

        >>> BalloonGraph.from_data_string(
        ...     "[a | 0, 1, 2 | 3 × A(0, 1) + A(1, 2)], [2, 3 | A(2, 3)]", str, int
        ... )
        Traceback (most recent call last):
        ...
        ValueError: the string '2, 3 | A(2, 3)'
        is not of the expected format '{balloon} | {nodes} | {hyperedges}'
        """
        anklet_graphs = []
        if data[0] != '[' or data[-1] != ']':
            raise ValueError(
                "data for individual anklet graphs must be enclosed by '[]' and separated by ', '"
            )
        for ag in data[1:-1].split('], ['):
            if ag.count(' | ') != 2:
                raise ValueError(
                    f"the string '{ag}'\n"
                    "is not of the expected format '{balloon} | {nodes} | {hyperedges}'"
                )
            balloon, nodes, hyperedges = ag.split(' | ')
            anklet_graphs.append(
                AnkletGraph.from_data_strings(
                    nodes,
                    hyperedges,
                    node_interpreter,
                    balloon=balloon_interpreter(balloon)
                )
            )
        return cls(*anklet_graphs)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Meta
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def name(self) -> str:
        """The name of the balloon graph."""
        return self._name

    @name.setter
    def name(self, s: str) -> None:
        self._name = s

    @property
    def attributes(self) -> dict[str, Any]:
        """The attributes of the anklet graph.

        Changes to the returned dictionary modify this balloon graphs's attributes.
        Assigning a mapping replaces the dictionary with a shallow copy of that mapping.
        """
        return self._attr

    @attributes.setter
    def attributes(self, value: Mapping[str, Any]) -> None:
        self._attr = dict(value)

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return set().union(*[ag.nodes for ag in self])

    def copy(self) -> Self:
        """Return a copy of the balloon graph.

        Balloon graph attributes and each anklet graph is copied. If the balloon graph
        has a name then '-copy' is appended: otherwise the copy remains unnamed.

        Returns
        -------
        Self
            A copy of the balloon graph.
        """
        return type(self)(
            *[ag.copy() for ag in self],
            name=self.name + '-copy' if self.name else '',
            **self._attr.copy()
        )

    def get_data_string(self) -> str:
        """Return a string summarizing the anklet graph data of the balloon graph.

        The balloon attribute and two data strings of each anklet graph are formated
        as `"[{ballon} | {nodes} | {hyperedges}]"` and then joined via `", "`.

        Returns
        -------
        str
            String encoding of the data needed to reconstruct the balloon graph.

        Raises
        ------
        ValueError
            If an anklet graph does not have a 'balloon' attribute.

        Examples
        --------
        >>> from inflated_graphs import Anklet
        >>> ag1 = AnkletGraph(range(0, 4), {Anklet(0, 1): 1, Anklet(1, 2, 3): 2}, balloon='a')
        >>> ag2 = AnkletGraph(range(4, 7), {Anklet(4, 5): 3})
        >>> BalloonGraph(ag1, ag2).get_data_string()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graph at index 1 does not have a 'balloon' attribute
        >>> ag2.attributes['balloon'] = 'b'
        >>> BalloonGraph(ag1, ag2).get_data_string()
        '[a | 0, 1, 2, 3 | A(0, 1) + 2 × A(1, 2, 3)], [b | 4, 5, 6 | 3 × A(4, 5)]'
        """
        self._check_balloon_attributes()
        return ", ".join(
            '[' + " | ".join([str(ag.attributes['balloon']), *ag.get_data_strings()]) + ']'
            for ag in self
        )

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graph operations
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def reduce(self) -> None:
        """Reduce each anklet graph: see :meth:`AnkletGraph.reduce`."""
        for ag in self:
            ag.reduce()

    def _combine(self, i: int, j: int) -> None:
        """Combine two anklet graphs.

        The anklet graphs at indices `i` and `j` must (i) belong to different balloons and
        (ii) have no nodes in common. Note that (ii) follows from (i) if the balloon graph
        has valid structure (see :meth:`BalloonGraph.check_structure`).

        In order, the following changes are made:
        - The graph at index `i` is replaced by the *disjoint* union
        of itself and the graph at index `j`
        - The anklet graphs in the same balloon as that at index `j` have their balloon attributes
        updated to match that of the graph at index `i`.
        - The graph at index `j` is removed.

        Note that since the disjoint union produces an anklet graph which is not connected,
        the balloon graph will *not* have a valid structure after calling this method.

        Parameters
        ----------
        i, j : int
            Indicies for the anklet graphs to combine.

        Raises
        ------
        ValueError
            If `i == j`, if any anklet graph does not have a 'balloon' attribute
            or if anklet graph `i` and anklet graph `j` belong to the same balloon.

        Examples
        --------
        >>> g = BalloonGraph.from_data_string(
        ...     "[a | 0, 1 | A(0, 1)], "
        ...     "[b | 2, 3, 4 | A(2, 3, 4)], "
        ...     "[c | 5, 6 | 3 × A(5, 6)], "
        ...     "[c | 6, 7 | A(6, 7)]",
        ...     str, int
        ... )
        >>> g._combine(0, 2)
        >>> print(g.get_data_string())
        [a | 0, 1, 5, 6 | A(0, 1) + 3 × A(5, 6)], [b | 2, 3, 4 | A(2, 3, 4)], [a | 6, 7 | A(6, 7)]
        """
        if i == j:
            raise ValueError('i and j must be distinct')

        # Ensure all anklet graphs have a 'balloon' attribute
        self._check_balloon_attributes()

        balloon_i = self[i].attributes['balloon']
        balloon_j = self[j].attributes['balloon']

        if balloon_i == balloon_j:
            raise ValueError(f"graphs {i} and {j} do not belong to different balloons")

        self[i] = anklet_graph_disjoint_union(self[i], self[j])

        for ag in self:
            if ag.attributes['balloon'] == balloon_j:
                ag.attributes['balloon'] = balloon_i
        self.pop(j)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Incidence
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def incidence(self) -> dict[T, set[int]]:
        """Return the incidence data.

        Returns
        -------
        dict[T, set[int]]
            Dictionary keyed by nodes.
            Values are the sets of indices for the anklet graphs containing that node.

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
        """Return the simple graph reflecting node / anklet graph incidences in the balloon graph.

        The returned graph has the *nodes* and *anklet graphs* of the balloon graph for nodes
        and edges between "node" nodes and "anklet graphs" nodes when a node belongs
        to an anklet graph: this is a simple, bipartite graph.

        All nodes in the returned bipartite graph are integers: "node" nodes have an attribute
        with name 'node' which stores the corresponding balloon graph nodes. Nodes without a 'node'
        attribute are "anklet graph" nodes and are simply the integer index into the balloon graph.

        Returns
        -------
        networkx.Graph
            A simple, bipartite graph on the nodes and anklet graphs of the balloon graph.

        See Also
        --------
        :meth:`incidence`
        """
        # Add integer nodes to the graph:
        # - For "anklet graph" nodes use the indices of the anklet graphs
        # - For "node" nodes just use the next 'n' integers (store the correspondence in 'node_ids')
        g = nx.Graph()
        g.add_nodes_from(range(len(self)))
        node_ids = {n: i for i, n in enumerate(self.nodes, start=len(self))}
        g.add_nodes_from((i, {'node': n}) for n, i in node_ids.items())

        # Add edges between "anklet graph" nodes and "node" nodes when one contains the other
        for i, ag in enumerate(self):
            for n in ag:
                g.add_edge(i, node_ids[n])

        return g

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _get_structure_hash(self) -> int:
        """Return a hash used in :meth:`BalloonGraph.check_structure` to determine if the balloon
        graph's structure has changed since the last validation.
        """
        return hash(self.get_data_string())

    def _reset_valid_structure(self) -> None:
        """Force a full validation on the next call of :meth:`BalloonGraph.check_structure`."""
        self._valid_structure = None

    def _check_balloon_attributes(self) -> None:
        """Validate that all anklet graphs belong to balloons.

        Returns quietly if all anklet graphs are assigned to balloons.

        Raises
        ------
        ValueError
            If one of the anklet graphs does not have a 'balloon' attribute.
        """
        for i, ag in enumerate(self):
            if 'balloon' not in ag.attributes:
                raise ValueError(
                    f"the anklet graph at index {i} does not have a 'balloon' attribute"
                )

    def _check_anklet_graph_structure(self, i: int) -> None:
        """Validate the structure of the `i`ᵗʰ anklet graph.

        Checks if the anklet graph (i) is non-empty, (ii) has a 'balloon' attribute,
        (iii) is connected and (iv) is planar.

        Returns silently if the structure of the `i`ᵗʰ anklet graph is valid.

        Raises
        ------
        ValueError
            If one of the four requirements above is not met (a short message explains the issue).
        """
        if not self[i].nodes:
            raise ValueError(f"the anklet graph at index {i} is empty")

        if 'balloon' not in self[i].attributes:
            raise ValueError(
                f"the anklet graph at index {i} does not have a 'balloon' attribute"
            )

        if not self[i].is_connected():
            raise ValueError(f"the anklet graph at index {i} is not connected")

        if not self[i].is_planar():
            raise ValueError(f"the anklet graph at index {i} is not planar")

    def check_structure(self) -> None:
        """Validate the structure of the balloon graph.

        Several conditions must be met for the structure of a balloon graph to be considered valid:
        - All anklet graphs must be non-empty, connected and planar.
        - If an anklet graph has a single node then that node does not appear in any other.
        - The anklet graphs have 'balloon' attributes which are equal for pairs which share a node.
        - The *incidence* graph, with nodes both the nodes and anklet graphs of the balloon graph
        and with edges between "node" nodes and "anklet graph" nodes when that anklet graph contains
        that node, is acyclic (i.e. a forest graph).

        Returns quietly if the structure is valid.

        Raises
        ------
        ValueError
            If any of the above conditions are not met (a short message explains the issue).

        Examples
        --------
        >>> from inflated_graphs import Anklet
        >>> g1 = AnkletGraph(hyperedges=[Anklet(0, 1, 2)], balloon='a')
        >>> g2 = AnkletGraph(hyperedges=[Anklet(2, 3, 4)])
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graph at index 1 does not have a 'balloon' attribute
        >>> g2.attributes['balloon'] = 'b'
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graphs containing node 2 (indices: [0, 1])
        do not all have the same value for their 'balloon' attribute
        >>> g2.attributes['balloon'] = 'a'
        >>> BalloonGraph(g1, g2).check_structure()  # Valid structure
        >>> g2.add_hyperedge(Anklet(1, 2))
        >>> BalloonGraph(g1, g2).check_structure()
        Traceback (most recent call last):
        ...
        ValueError: Invalid structure. the node / anklet graph incidence graph contains the cycle
        (graph 0) → (node 1) → (graph 1) → (node 2) → (graph 0)
        """
        if self._get_structure_hash() == self._valid_structure:
            # If the hash has not changed since the last successful structure check,
            # there is no need to check again
            return

        # Check the structure of individual anklet graphs
        for i in range(len(self)):
            try:
                self._check_anklet_graph_structure(i)
            except ValueError as exc:
                self._reset_valid_structure()
                raise exc

        # Check the structure of the incidence graph...
        inc_graph = self.to_incidence_graph()

        # 1) If an anklet graph has a single node then that node is not contained in any others.
        for i, ag in enumerate(self):
            if len(ag.nodes) == 1:
                # The node 'n' of 'g' corresponds to the unique node of 'ag'. It should only have
                # one neighbor in the incidence graph, namely node 'i' (corresponding to 'ag')
                n = list(inc_graph.adj[i])[0]
                if set(inc_graph.adj[n]) != {i}:
                    self._reset_valid_structure()
                    raise ValueError(
                        f"the anklet graph at index {i} has only one node {ag.nodes}"
                        f"\nand this node appears in multiple anklet graphs: {inc_graph.adj[n]}"
                    )

        # 2) For each node the anklet graphs containing it must have the same value for 'balloon'.
        for i in inc_graph:
            if 'node' in inc_graph.nodes[i]:
                if len({self[j].attributes['balloon'] for j in inc_graph.neighbors(i)}) != 1:
                    self._reset_valid_structure()
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
            self._reset_valid_structure()
            raise ValueError(
                "Invalid structure. the node / anklet graph incidence graph contains the cycle\n" +
                " → ".join([*cycle_data, cycle_data[0]])
            )

        # The structure is valid:
        # save the hash to avoid checking the structure again if it doesn't change
        self._valid_structure = self._get_structure_hash()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Balloon components
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _balloon_components(self) -> list[set[T]]:
        self._check_balloon_attributes()

        balloons: list[tuple[Any, set[T]]] = []
        for ag in self:
            id_found = False
            for i, (balloon_id, balloon_nodes) in enumerate(balloons):
                if ag.attributes['balloon'] == balloon_id:
                    id_found = True
                    balloons[i] = (balloon_id, balloon_nodes.union(ag.nodes))
                    break
            if not id_found:
                balloons.append((ag.attributes['balloon'], ag.nodes))

        return [balloon_nodes for _, balloon_nodes in balloons]
