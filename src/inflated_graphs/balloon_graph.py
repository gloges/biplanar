"""Balloon graphs."""

from collections.abc import Callable, Hashable, Mapping
from typing import Any, Self
import networkx as nx
from .anklet_graph import AnkletGraph
from .anklet_graph_unions import disjoint_union as anklet_graph_disjoint_union


class BalloonGraph[T: Hashable](list[list[AnkletGraph[T]]]):
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str
    _attr: dict[str, Any]
    _valid_structure: int | None

    def __init__(self, *balloons: list[AnkletGraph[T]], name: str = "", **attr: Any) -> None:
        super().__init__(balloons)
        self._name = name
        self._attr = attr
        self._reset_valid_structure()

    @classmethod
    def from_data_string(cls, data: str, interpreter: Callable[[str], T]) -> Self:
        """Construct a balloon graph from a string summarizing its balloons and anklet graphs.

        The input string must follow the format produced by :meth:`BalloonGraph.get_data_string`.

        Parameters
        ----------
        data : str
            String encoding of the balloon graph.
        interpreter : Callable[[str], T]
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
        ...     "[<0, 1, 2 | 3 × A(0, 1) + A(1, 2)>, <2, 3 | A(2, 3)>], [<4 | >]", int
        ... )
        >>> for i, balloon in enumerate(g):
        ...    print(f"balloon {i}:")
        ...    for ag in balloon:
        ...        print('   ', str(ag.nodes).ljust(9), ag.hyperedges)
        balloon 0:
            {0, 1, 2} ((A(0, 1), 3), (A(1, 2), 1))
            {2, 3}    ((A(2, 3), 1),)
        balloon 1:
            {4}       ()
        """
        balloons = []
        if data:
            if data[0] != '[' or data[-1] != ']':
                raise ValueError(
                    "data for each ballon must be enclosed by '[ ]' and separated by ', '"
                )
            for balloon_data in data[1:-1].split('], ['):
                if balloon_data[0] != '<' or balloon_data[-1] != '>':
                    raise ValueError(
                        "data for each anklet graph in a balloon must"
                        " be enclosed by '< >' and separated by ', '"
                    )

                balloon = []
                for anklet_graph_data in balloon_data[1:-1].split('>, <'):
                    if anklet_graph_data.count(' | ') != 1:
                        raise ValueError(
                            f"the string '{anklet_graph_data}'\n"
                            "is not of the expected format '{nodes} | {hyperedges}'"
                        )
                    nodes, hyperedges = anklet_graph_data.split(' | ')
                    balloon.append(
                        AnkletGraph.from_data_strings(nodes, hyperedges, interpreter)
                    )
                balloons.append(balloon)

        return cls(*balloons)

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
        return set().union(*[ag.nodes for balloon in self for ag in balloon])

    def balloon_nodes(self) -> list[set[T]]:
        """The sets of nodes in each balloon."""
        return [set().union(*[ag.nodes for ag in balloon]) for balloon in self]

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
            *[[ag.copy() for ag in balloon] for balloon in self],
            name=self.name + '-copy' if self.name else '',
            **self._attr.copy()
        )

    def get_data_string(self) -> str:
        """Return a string summarizing the balloons and anklet graphs of the balloon graph.

        The data strings for each anklet graph are formated as `<{nodes} | {hyperedges}>`
        (using the strings produced by :meth:`AnkletGraph.get_data_strings()`).
        These are then collected into brackets by balloon and joined by commas:
        `[<{nodes_0} | {hyperedges_0}>, <{nodes_1} | {hyperedges_1}>, ...], [...], ...`.

        Returns
        -------
        str
            An encoding of the balloon graph.

        Examples
        --------
        >>> from inflated_graphs import Anklet
        >>> ag1 = AnkletGraph(range(0, 3), {Anklet(0, 1): 1, Anklet(0, 1, 2): 2})
        >>> ag2 = AnkletGraph(range(3, 6), {Anklet(3, 4): 3})
        >>> ag3 = AnkletGraph(range(6, 9), {Anklet(6, 7, 8)})
        >>> BalloonGraph([ag1, ag2], [ag3]).get_data_string()
        '[<0, 1, 2 | A(0, 1) + 2 × A(0, 1, 2)>, <3, 4, 5 | 3 × A(3, 4)>], [<6, 7, 8 | A(6, 7, 8)>]'
        """
        return ", ".join([
            '[' + ", ".join(['<' + " | ".join(ag.get_data_strings()) + '>' for ag in balloon]) + ']'
            for balloon in self
        ])

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graph operations
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def reduce(self) -> None:
        """Reduce each anklet graph: see :meth:`AnkletGraph.reduce`."""
        for balloon in self:
            for ag in balloon:
                ag.reduce()

    def _combine(self, pos_a: tuple[int, int], pos_b: tuple[int, int]) -> None:
        """Combine two anklet graphs.

        The two anklet graphs at positions `pos_a` and `pos_b` must be in different balloons
        (*i.e.* the zeroth elements of `pos_a` and `pos_b` must be different) and have no nodes
        in common. Note that the latter condition follows from the former if the balloon graph
        has valid structure (see :meth:`BalloonGraph.check_structure`).

        In order, the following changes are made:
        - The anklet graph at position `pos_a` is replaced by the *disjoint* union
        of itself and the anklet graph at position `pos_b`.
        - The anklet graph at position `pos_b` is removed.
        - The anklet graphs of balloon `b` are moved into balloon `a`.
        - Balloon `b` is removed.

        Note that since the disjoint union produces an anklet graph which is not connected,
        the balloon graph will *not* have a valid structure after calling this method.

        Parameters
        ----------
        pos_a, pos_b : tuple[int, int]
            Positions of the two anklet graphs to be combined.

        Raises
        ------
        ValueError
            If the anklet graphs at positions `pos_a` and `pos_b`
            are in the same balloon or share a node.

        Examples
        --------
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1 | A(0, 1)>], "
        ...     "[<2, 3, 4 | A(2, 3, 4)>], "
        ...     "[<5, 6 | 3 × A(5, 6)>, <6, 7 | A(6, 7)>]",
        ...     int
        ... )
        >>> g._combine((0, 0), (2, 0))
        >>> print(g.get_data_string())
        [<0, 1, 5, 6 | A(0, 1) + 3 × A(5, 6)>, <6, 7 | A(6, 7)>], [<2, 3, 4 | A(2, 3, 4)>]
        """
        balloon_a, index_a = pos_a
        balloon_b, index_b = pos_b

        if balloon_a == balloon_b:
            raise ValueError(f'the positions {pos_a} and {pos_b} point to the same balloon')

        self[balloon_a][index_a] = anklet_graph_disjoint_union(
            self[balloon_a][index_a],
            self[balloon_b][index_b]
        )
        self[balloon_b].pop(index_b)
        self[balloon_a].extend(self[balloon_b])
        self.pop(balloon_b)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Incidence
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def incidence(self) -> dict[T, set[tuple[int, int]]]:
        """Return the incidence data.

        Returns
        -------
        dict[T, set[tuple[int, int]]]
            Dictionary keyed by nodes. Values are the sets of index pairs giving
            the positions of the anklet graphs containing that node.

        See Also
        --------
        :meth:`to_incidence_graph`
        """
        inc = {n: set() for n in self.nodes}
        for i, balloon in enumerate(self):
            for j, ag in enumerate(balloon):
                for n in ag.nodes:
                    inc[n].add((i, j))
        return inc

    def to_incidence_graph(self) -> nx.Graph:
        """Return the simple graph reflecting node / anklet graph incidences in the balloon graph.

        The returned graph has the *nodes* and *anklet graphs* of the balloon graph for nodes
        and edges between "node" nodes and "anklet graphs" nodes when a node belongs
        to an anklet graph: this is a simple, bipartite graph.

        "Node" nodes in the returned bipartite graph are integers and have an attribute with name
        'node' storing the corresponding node from the balloon graph. "Anklet graph" nodes
        are pairs of integers giving the position of the anklet graph in the balloon graph.

        Returns
        -------
        networkx.Graph
            A simple, bipartite graph on the nodes and anklet graphs of the balloon graph.

        See Also
        --------
        :meth:`incidence`
        """
        g = nx.Graph()
        node_ids = {n: i for i, n in enumerate(self.nodes)}
        g.add_nodes_from((i, {'node': n}) for n, i in node_ids.items())
        g.add_nodes_from((i, j) for i, balloon in enumerate(self) for j in range(len(balloon)))

        # Add edges between "anklet graph" nodes and "node" nodes when one contains the other
        for i, balloon in enumerate(self):
            for j, ag in enumerate(balloon):
                for n in ag:
                    g.add_edge((i, j), node_ids[n])

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

    def _check_anklet_graph_structure(self, pos: tuple[int, int]) -> None:
        """Validate the structure of an anklet graph.

        Checks if the anklet graph (i) is non-empty, (ii) is connected and (iii) is planar.

        Returns silently if the structure of the anklet graph is valid.

        Raises
        ------
        ValueError
            If one of the three requirements above is not met (a short message explains the issue).
        """
        balloon, index = pos
        anklet_graph = self[balloon][index]

        if not anklet_graph.nodes:
            self._reset_valid_structure()
            raise ValueError(f"the anklet graph at position {pos} is empty")

        if not anklet_graph.is_connected():
            self._reset_valid_structure()
            raise ValueError(f"the anklet graph at position {pos} is not connected")

        if not anklet_graph.is_planar():
            self._reset_valid_structure()
            raise ValueError(f"the anklet graph at position {pos} is not planar")

    def _check_node_monogamy(self) -> None:
        """Validates that each node appears in only one balloon.

        Returns silently if each node is "monogamous".

        Raises
        ------
        ValueError
            If a node appears in two (or more) anklet graphs belonging to different balloons.
        """
        node_balloons = {}
        for i, balloon in enumerate(self):
            for ag in balloon:
                for n in ag:
                    if n not in node_balloons:
                        node_balloons[n] = i
                    elif node_balloons[n] != i:
                        self._reset_valid_structure()
                        raise ValueError(
                            f"the node '{n}' appears in at least two balloons"
                            f" ({node_balloons[n]} and {i})"
                        )

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
        """Returns sets of nodes which belong to anklet graphs with common 'balloon' attribute.

        Note that a node may appear in multiple balloons if the structure is invalid.

        Returns
        -------
        list[set[T]]
            Sets of nodes belonging to the same balloon.
            If the balloon graph has valid structure then these sets are disjoint.

        Raises
        ------
        ValueError
            If one of the anklet graphs does not have a 'balloon' attribute.

        Examples
        --------
        A typical use case with a balloon graph with valid structure:

        >>> g = BalloonGraph.from_data_string(
        ...     "[a | 0, 1 | A(0, 1)], "
        ...     "[b | 2, 3, 4 | A(2, 3, 4)], "
        ...     "[c | 5, 6 | 3 × A(5, 6)], "
        ...     "[c | 6, 7 | A(6, 7)]",
        ...     str, int
        ... )
        >>> g._balloon_components()
        [{0, 1}, {2, 3, 4}, {5, 6, 7}]

        In a balloon graph with invalid structure the returned node sets may not be disjoint:

        >>> g = BalloonGraph.from_data_string(
        ...     "[a | 0, 1 | A(0, 1)], [b | 1, 2, 3 | A(1, 2) + 3 × A(2, 3)]", str, int
        ... )
        >>> g._balloon_components()
        [{0, 1}, {1, 2, 3}]
        """
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
