"""Balloon graphs."""

from __future__ import annotations
from collections.abc import Callable, Hashable, Iterator, Mapping
from itertools import combinations, product
from types import NotImplementedType
from typing import Any, Self
import networkx as nx
from .anklet import Anklet
from .anklet_graph import AnkletGraph
from .union import disjoint_union
from .zipper import zipper

type IndexPair = tuple[int, int]  # (balloon index, anklet graph index)


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
        ...        print('   ', ag.data_string())
        balloon 0:
            <0, 1, 2 | 3 × A(0, 1) + A(1, 2)>
            <2, 3 | A(2, 3)>
        balloon 1:
            <4 | >
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
                balloons.append([
                    AnkletGraph.from_data_string('<' + anklet_graph_data + '>', interpreter)
                    for anklet_graph_data in balloon_data[1:-1].split('>, <')
                ])

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
        """The attributes of the balloon graph.

        Changes to the returned dictionary modify this balloon graphs's attributes.
        Assigning a mapping replaces the dictionary with a shallow copy of that mapping.
        """
        return self._attr

    @attributes.setter
    def attributes(self, value: Mapping[str, Any]) -> None:
        self._attr = dict(value)

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

    def data_string(self) -> str:
        """Return a string summarizing the balloons and anklet graphs of the balloon graph.

        The data strings for each anklet graph are of the form
        `<{nodes} | {hyperedges}>` (see :meth:`AnkletGraph.data_string()`).
        These are collected into brackets by balloon and joined by commas:
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
        >>> BalloonGraph([ag1, ag2], [ag3]).data_string()
        '[<0, 1, 2 | A(0, 1) + 2 × A(0, 1, 2)>, <3, 4, 5 | 3 × A(3, 4)>], [<6, 7, 8 | A(6, 7, 8)>]'
        """
        return ", ".join([
            '[' + ", ".join([ag.data_string() for ag in balloon]) + ']'
            for balloon in self
        ])

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Balloons, anklet graphs and nodes
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def number_of_balloons(self) -> int:
        """Return the number of balloons (equivalent to `len(g)`)."""
        return len(self)

    def number_of_anklet_graphs(self, i: int | None = None) -> int:
        """Return the number of anklet graphs.

        If `i` is an integer then returns the number of anklet graphs
        in the `i`ᵗʰ balloon (*i.e.* `len(self[i])`). Otherwise, returns
        the total number of anklet graphs across all balloons.

        Parameters
        ----------
        i : int or None, optional (default=None)
            The balloon index.

        Returns
        -------
        int
            If `i` is an integer, the number of anklet graphs in balloon `i`.
            Otherwise, the total number of anklet graphs.
        """
        if isinstance(i, int):
            return len(self[i])
        return sum(len(balloon) for balloon in self)

    def iter_anklet_graphs(self) -> Iterator[tuple[IndexPair, AnkletGraph[T]]]:
        """Yield (location, anklet_graph) pairs.

        'Locations' are pairs of indices, the first gives the balloon
        and the second the anklet graph within that balloon.
        """
        for i, balloon in enumerate(self):
            for j, ag in enumerate(balloon):
                yield (i, j), ag

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return set().union(*[ag.nodes for balloon in self for ag in balloon])

    def balloon_nodes(self, i: int) -> set[T]:
        """The set of nodes in the `i`ᵗʰ balloon."""
        return set().union(*[ag.nodes for ag in self[i]])

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graph operations
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def reduce(self) -> None:
        """Reduce each anklet graph: see :meth:`AnkletGraph.reduce`."""
        for _, ag in self.iter_anklet_graphs():
            ag.reduce()

    def prune_subsingleton(self) -> None:
        """Selectively remove anklet graphs and balloons.

        Removes (i) empty anklet graphs, (ii) 1-node anklet graphs whose node appears in another
        anklet graph of the *same* balloon and (iii) empty balloons.

        Examples
        --------
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1, 2 | A(0, 1, 2)>, <2 | >, <3 | >], [<4 | >, < | >, <4 | >], [< | >]", int
        ... )
        >>> g.prune_subsingleton()
        >>> g.data_string()
        '[<0, 1, 2 | A(0, 1, 2)>, <3 | >], [<4 | >]'
        """
        for (i, j), ag in reversed(list(self.iter_anklet_graphs())):
            if not ag.nodes or (
                ag.number_of_nodes() == 1
                and any(ag.nodes <= ag2.nodes for j2, ag2 in enumerate(self[i]) if j != j2)
            ):
                self[i].pop(j)

        for i, balloon in reversed(list(enumerate(self))):
            if not balloon:
                self.pop(i)

    def combine_anklet_graphs(self, loc_a: IndexPair, loc_b: IndexPair) -> IndexPair:
        """Combine two anklet graphs.

        `loc_a` and `loc_b` give the locations of anklet graphs in the balloon graph:
        the first element of each gives the balloon index and second element the anklet graph index
        within that balloon.

        The two anklet graphs must be in different balloons and have no nodes in common.
        Note that the latter condition follows from the former if the balloon graph
        has a valid structure (see :meth:`BalloonGraph.check_structure`).

        In order, the following changes are made:
        - The anklet graph at location `loc_a` is replaced by the *disjoint* union
        of itself and the anklet graph at location `loc_b`.
        - The anklet graph at location `loc_b` is removed.
        - The anklet graphs of balloon `b` are moved into balloon `a`.
        - Balloon `b` is removed.

        **Note**: since the disjoint union produces an anklet graph which is not connected,
        the balloon graph will *not* have a valid structure after calling this method.

        Parameters
        ----------
        loc_a, loc_b : IndexPair
            Index pairs giving the location for the two anklet graphs to be combined.

        Returns
        -------
        IndexPair
            The final location of the combined anklet graph after the above operations:
            returns `loc_a` if `loc_a[0] < loc_b[0]`, otherwise returns `(loc_a[0] - 1, loc_a[1])`.

        Raises
        ------
        ValueError
            If the anklet graphs at locations `loc_a` and `loc_b`
            are in the same balloon or share a node.

        Examples
        --------
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1 | A(0, 1)>], "
        ...     "[<2, 3, 4 | A(2, 3, 4)>], "
        ...     "[<5, 6 | 3 × A(5, 6)>, <6, 7 | A(6, 7)>]",
        ...     int
        ... )
        >>> g.combine_anklet_graphs((0, 0), (2, 0))
        (0, 0)
        >>> g.data_string()
        '[<0, 1, 5, 6 | A(0, 1) + 3 × A(5, 6)>, <6, 7 | A(6, 7)>], [<2, 3, 4 | A(2, 3, 4)>]'
        """
        i_a, j_a = loc_a
        i_b, j_b = loc_b

        if i_a == i_b:
            raise ValueError(f'the anklet graphs at {loc_a} and {loc_b} belong to the same balloon')

        self[i_a][j_a] = disjoint_union(
            self[i_a][j_a],
            self[i_b][j_b]
        )
        self[i_b].pop(j_b)
        self[i_a].extend(self[i_b])
        self.pop(i_b)

        return (i_a, j_a) if i_a < i_b else (i_a - 1, j_a)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Incidence / adjacency
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def incidence(self) -> dict[T, set[IndexPair]]:
        """Return the incidence data.

        Returns
        -------
        dict[T, set[IndexPair]]
            Dictionary keyed by nodes. Values are the sets of index pairs giving
            the locations of the anklet graphs containing that node.

        See Also
        --------
        :meth:`to_incidence_graph`,
        :meth:`anklet_graph_adjacency`,
        :meth:`anklet_adjacent_pairs`
        """
        inc = {n: set() for n in self.nodes}
        for loc, ag in self.iter_anklet_graphs():
            for n in ag.nodes:
                inc[n].add(loc)
        return inc

    def to_incidence_graph(self) -> tuple[nx.Graph, dict[T, int]]:
        """Return the simple graph reflecting node / anklet graph incidences in the balloon graph.

        The returned graph has the *nodes* and *anklet graphs* of the balloon graph for nodes
        and edges between "node" nodes and "anklet graphs" nodes when a node belongs
        to an anklet graph: this is a simple, bipartite graph.

        "Node" nodes in the returned bipartite graph are integers and have an attribute with name
        'node' storing the corresponding node from the balloon graph. "Anklet graph" nodes
        are pairs of integers giving the locations of the anklet graph in the balloon graph.

        Returns
        -------
        networkx.Graph
            A simple, bipartite graph on the nodes and anklet graphs of the balloon graph.
        dict[T, int]
            A dictionary keyed by the nodes of the balloon graph and with values the corresponding
            integer nodes of the returned bipartite incidence graph.

        See Also
        --------
        :meth:`incidence`,
        :meth:`anklet_graph_adjacency`,
        :meth:`anklet_adjacent_pairs`
        """
        g = nx.Graph()
        node_ids = {n: i for i, n in enumerate(self.nodes)}
        g.add_nodes_from((i, {'node': n}) for n, i in node_ids.items())
        g.add_nodes_from(loc for loc, _ in self.iter_anklet_graphs())

        # Add edges between "anklet graph" nodes and "node" nodes when one contains the other
        for loc, ag in self.iter_anklet_graphs():
            for n in ag:
                g.add_edge(loc, node_ids[n])

        return g, node_ids

    def anklet_graph_adjacency(self) -> dict[IndexPair, set[IndexPair]]:
        """Return the adjacency data.

        Two anklet graphs are adjacent if they share a node.
        Note that if the balloon graph has valid structure then an anklet graph
        can only be adjacent to anklet graphs within its balloon.

        Returns
        -------
        dict[IndexPair, set[IndexPair]]
            Dictionary keyed by anklet graph locations.
            Values are the sets of locations of adjacent anklet graphs.

        See Also
        --------
        :meth:`incidence`,
        :meth:`to_incidence_graph`,
        :meth:`anklet_adjacent_pairs`

        Examples
        --------
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1 | A(0, 1)>, <1, 2, 3 | A(1, 3) + A(2, 3)>], [<4, 5, 6 | A(4, 5, 6)>]", int
        ... )
        >>> g.anklet_graph_adjacency()
        {(0, 0): {(0, 1)}, (0, 1): {(0, 0)}, (1, 0): set()}
        """
        adj = {loc: set() for loc, _ in self.iter_anklet_graphs()}
        for (loc_1, ag_1), (loc_2, ag_2) in combinations(self.iter_anklet_graphs(), r=2):
            if ag_1.nodes & ag_2.nodes:
                adj[loc_1].add(loc_2)
                adj[loc_2].add(loc_1)
        return adj

    def anklet_adjacent_pairs(self) -> set[tuple[T, T]]:
        """Collect all pairs of nodes which are adjacent in one or more hyperedge.

        Returns
        -------
        set[tuple[T, T]]
            All pairs of adjacent nodes.

        See Also
        --------
        :meth:`incidence`,
        :meth:`to_incidence_graph`,
        :meth:`anklet_graph_adjacency`

        Examples
        --------
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1 | A(0, 1)>, <1, 2, 3 | A(1, 3) + A(2, 3)>], [<4, 5, 6 | A(4, 5, 6)>]", int
        ... )
        >>> sorted(g.anklet_adjacent_pairs())
        [(0, 1), (1, 3), (2, 3), (4, 5), (4, 6), (5, 6)]
        """
        adjacent_pairs = set()
        for _, ag in self.iter_anklet_graphs():
            for u, nbrs in ag.anklet_adjacency().items():
                for v in nbrs:
                    if (u, v) not in adjacent_pairs and (v, u) not in adjacent_pairs:
                        adjacent_pairs.add((u, v))
        return adjacent_pairs

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _get_structure_hash(self) -> int:
        """Return a hash used in :meth:`BalloonGraph.check_structure` to determine if the balloon
        graph's structure has changed since the last validation.
        """
        return hash(self.data_string())

    def _reset_valid_structure(self) -> None:
        """Force a full validation on the next call of :meth:`BalloonGraph.check_structure`."""
        self._valid_structure = None

    def _check_anklet_graph_structure(self, loc: IndexPair) -> None:
        """Validate the structure of an anklet graph.

        Checks if the anklet graph (i) is non-empty, (ii) is connected and (iii) is planar.

        Returns silently if the structure of the anklet graph is valid.

        Raises
        ------
        ValueError
            If one of the three requirements above is not met (a short message explains the issue).
        """
        i, j = loc
        anklet_graph = self[i][j]

        if not anklet_graph.nodes:
            self._reset_valid_structure()
            raise ValueError(f"the anklet graph at {loc} is empty")

        if not anklet_graph.is_connected():
            self._reset_valid_structure()
            raise ValueError(f"the anklet graph at {loc} is not connected")

        if not anklet_graph.is_planar():
            self._reset_valid_structure()
            raise ValueError(f"the anklet graph at {loc} is not planar")

    def _check_node_monogamy(self) -> None:
        """Validates that each node appears in only one balloon.

        Returns silently if each node is "monogamous".

        Raises
        ------
        ValueError
            If a node appears in two (or more) anklet graphs belonging to different balloons.
        """
        node_balloons = {}
        for (i, _), ag in self.iter_anklet_graphs():
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
        - Each anklet graphs is non-empty, connected and planar.
        - The sets of nodes contained in each balloon are disjoint.
        - If an anklet graph has a single node then that node
        does not appear in any other anklet graph.
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
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1, 2 | 3 × A(0, 1, 2)>, < | >], [<3 | >]", int
        ... )
        >>> g.check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graph at (0, 0) is not planar
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1, 2 | 2 × A(0, 1, 2)>, < | >], [<3 | >]", int
        ... )
        >>> g.check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graph at (0, 1) is empty
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1, 2 | 2 × A(0, 1, 2)>, <2 | >], [<3 | >]", int
        ... )
        >>> g.check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the anklet graph at (0, 1) has only one node
        which also appears in the anklet graph at (0, 0)
        >>> g = BalloonGraph.from_data_string(
        ...     "[<0, 1, 2 | 2 × A(0, 1, 2)>, <2, 3 | A(2, 3)>], [<3 | >]", int
        ... )
        >>> g.check_structure()
        Traceback (most recent call last):
        ...
        ValueError: the node '3' appears in at least two balloons (0 and 1)
        """
        if self._get_structure_hash() == self._valid_structure:
            # If the hash has not changed since the last successful structure check,
            # there is no need to check again
            return

        for loc, _ in self.iter_anklet_graphs():
            self._check_anklet_graph_structure(loc)

        self._check_node_monogamy()

        for (i, j), ag in self.iter_anklet_graphs():
            if len(ag.nodes) == 1:
                for j2, ag2 in enumerate(self[i]):
                    if j != j2 and ag.nodes & ag2.nodes:
                        self._reset_valid_structure()
                        raise ValueError(
                            f"the anklet graph at ({i}, {j}) has only one node\n"
                            f"which also appears in the anklet graph at ({i}, {j2})"
                        )

        inc_graph, _ = self.to_incidence_graph()

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
    #   (In)equality
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def __le__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BalloonGraph):
            return NotImplemented
        return poset_le(self, other)

    def __ge__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BalloonGraph):
            return NotImplemented
        return poset_le(other, self)

    def __lt__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BalloonGraph):
            return NotImplemented
        return poset_le(self, other) and not poset_le(other, self)

    def __gt__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BalloonGraph):
            return NotImplemented
        return poset_le(other, self) and not poset_le(self, other)

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BalloonGraph):
            return NotImplemented
        return poset_eq(self, other)


# pylint: disable=too-many-return-statements,too-many-branches,too-many-locals,too-many-statements
def _poset_le_aux[T: Hashable](g: BalloonGraph[T], h: list[AnkletGraph[T]]) -> bool:
    """Return whether `g ≤ BalloonGraph(h)`.

    Both `g` and `BalloonGraph(h)` are assumed to have valid structure
    (see :meth:`BalloonGraph.check_structure`) and the same set of nodes.

    This function *defines* the relation `g₁ ≤ g₂` between balloon graphs
    when `g₂` has a single balloon and is defined recursively by making minimal changes
    to the two balloon graphs until a direct pair-wise comparison of anklet graphs is possible
    (using :meth:`AnkletGraph.__le__`).
    That the relation thus defined has the transitive property is non-trivial.

    **DO NOT** call this method directly: use :meth:`poset_le` or :meth:`BalloonGraph.__le__`
    instead as these check that the balloon graphs have valid structures and handle
    balloon graphs with more than one balloon.

    Parameters
    ----------
    g : BalloonGraph[T]
        A balloon graph with valid structure and the same nodes as `h`.
    h : list[AnkletGraph[T]]
        A list of anklet graphs such that `BalloonGraph(h)` has valid structure.

    Returns
    -------
    bool
        Whether `g` is embeddable into `BalloonGraph(h)`.
    """

    # If g and BalloonGraph(h) have the same incidence graphs (i.e. for every anklet graph
    # of g there is an anklet graph of h with exactly the same nodes, and vice versa)
    # then compare their anklet graphs in pairs (i.e. using AnkletGraph.__le__).
    # This is the "base case".
    if g.number_of_anklet_graphs() == len(h):
        # Same number of anklet graphs: look for an exact pairing based on node sets
        pairing = {}
        for loc, ag_g in g.iter_anklet_graphs():
            for k, ag_h in enumerate(h):
                if ag_g.nodes == ag_h.nodes:
                    # An exact match! Store the corresponding index
                    pairing[loc] = k
        if len(pairing) == len(h):
            # All anklet graphs of g have a corresponding anklet graph in h
            result = all(g[i][j] <= h[k] for (i, j), k in pairing.items())
            return result

    # The incidence graphs of g and BalloonGraph(h) differ.
    # In order to have g ≤ h it must be the case that for every pair of nodes u and v at finite
    # distance in the incidence graph of BalloonGraph(h) that either the distance between them
    # is shorter in the incidence graph of g or they are in separate balloons of g
    inc_graph_g, ids_g = g.to_incidence_graph()
    inc_graph_h, ids_h = BalloonGraph(h).to_incidence_graph()
    distances_g = dict(nx.all_pairs_shortest_path_length(inc_graph_g))
    distances_h = dict(nx.all_pairs_shortest_path_length(inc_graph_h))
    for u, v in combinations(g.nodes, r=2):
        if ids_h[v] in distances_h[ids_h[u]]:
            # Finite distance: u and v are in the same connected component of h
            if ids_g[v] not in distances_g[ids_g[u]]:
                # u and v are in different connected components of g
                # This is fine as long as these are different balloons
                if any({u, v} <= g.balloon_nodes(i) for i in range(len(g))):
                    return False
            else:
                # u and v are in the same connected component of g
                # If their distance for g is longer than it is for h then we do not have g ≤ h
                if distances_g[ids_g[u]][ids_g[v]] > distances_h[ids_g[u]][ids_g[v]]:
                    return False

    # At this point the incidence graphs of g and h differ
    # but there is no immediate issue that would prove "not g ≤ h".
    # The idea now is to make minimal changes, break into subcases, and use transitivity.

    # Check for pairs of nodes which are *directly* adjacent in g but are in different connected
    # components of h. If such a pair is found, say u and v, then a minimal change is to add
    # the anklet graph <u, v | A(u, v)> to h.
    for u, v in g.anklet_adjacent_pairs():
        if ids_h[v] not in distances_h[ids_h[u]]:
            # Remove the anklet graphs <u | > and <v | > if present and add <u, v | A(u, v)>
            h_augmented = [ag_h for ag_h in h if ag_h.nodes not in ({u}, {v})]
            h_augmented.append(AnkletGraph(hyperedges=[Anklet(u, v)]))
            return _poset_le_aux(g, h_augmented)

    # Scan through all pairs of *directly adjacent* nodes in h looking for a pair (u, v)
    # with u and v in different balloons in g. Keep track of the pair with this property
    # for which u and v appear in the fewest anklet graph of g
    # (this keeps the branching factor later as small as possible)
    min_branch_pair = None
    min_branching_factor = -1
    incidence_g = g.incidence()
    for u, v in BalloonGraph(h).anklet_adjacent_pairs():
        # Identify the balloons containing u and v (unique assuming valid structure of g)
        i_u = list(incidence_g[u])[0][0]
        i_v = list(incidence_g[v])[0][0]
        if i_u != i_v:
            # u and v appear in separate balloons of g: save as the min branch pair
            # if not yet assigned or if they appear in fewer anklet graphs than the current best
            js_u = {j for _, j in incidence_g[u]}
            js_v = {j for _, j in incidence_g[v]}
            if min_branch_pair is None or len(js_u) * len(js_v) < min_branching_factor:
                min_branch_pair = (u, v)
                min_branching_factor = len(js_u) * len(js_v)

    if min_branch_pair is not None:
        # u and v are in separate balloons of g but in a common anklet graph of h.
        # Branch over all ways to join the two balloons of g by combining two anklet graphs
        # containing u and v. These "g_joined"s are *strictly larger* than g and if any
        # one is less than or equal to h then also g ≤ h by transitivity.
        u, v = min_branch_pair
        for loc_u, loc_v in product(incidence_g[u], incidence_g[v]):
            g_joined = g.copy()
            i, j = g_joined.combine_anklet_graphs(loc_u, loc_v)
            g_joined[i][j].add_hyperedge(Anklet(u, v))
            if _poset_le_aux(g_joined, h):
                return True
        return False

    # At this point the connected components of g and h are the same

    # Check for a pair of anklet graphs which are distance 2 apart in the incidence graph of
    # BalloonGraph(h) (i.e. have a node in common) and split a pair of directly adjacent nodes in g
    g_adjacent_pairs = g.anklet_adjacent_pairs()
    for (i1, ag1_h), (i2, ag2_h) in combinations(enumerate(h), r=2):
        if ag1_h.nodes & ag2_h.nodes and any(
            {u, v} <= ag1_h.nodes | ag2_h.nodes and not ag1_h.nodes & ag2_h.nodes <= {u, v}
            for u, v in g_adjacent_pairs
        ):
            for zipped_ag in zipper(ag1_h, ag2_h):
                h_zipped = h.copy()
                h_zipped[i1] = zipped_ag
                h_zipped.pop(i2)
                if _poset_le_aux(g, h_zipped):
                    return True
            return False

    # Check for a pair of anklet graphs which are distance 2 apart in the incidence graph of
    # BalloonGraph(h) (i.e. have a node in common) and whose union of nodes is a subset of the nodes
    # of an anklet graph in g.
    for (i1, ag1_h), (i2, ag2_h) in combinations(enumerate(h), r=2):
        if ag1_h.nodes & ag2_h.nodes and any(
            ag1_h.nodes | ag2_h.nodes <= ag_g.nodes
            for _, ag_g in g.iter_anklet_graphs()
        ):
            for zipped_ag in zipper(ag1_h, ag2_h):
                h_zipped = h.copy()
                h_zipped[i1] = zipped_ag
                h_zipped.pop(i2)
                if _poset_le_aux(g, h_zipped):
                    return True
            return False

    # Raise an error to alert that something has gone wrong
    raise RuntimeError(
        "this point should not be reached if 'g' and 'h' have valid structure and the same nodes\n"
        f"  g = {g.data_string()}\n"
        f"  h = {BalloonGraph(h).data_string()}"
    )


def poset_le[T: Hashable](g: BalloonGraph[T], h: BalloonGraph[T]) -> bool:
    """Return whether `g` is *embeddable* into `h`.

    Parameters
    ----------
    g, h : BalloonGraph[T]
        Two balloon graphs on the same set of nodes.

    Returns
    -------
    bool
        Whether `g ≤ h`.

    Raises
    ------
    ValueError
        If `g` and `h` do not have the same nodes.
    """
    g.check_structure()
    h.check_structure()

    if g.nodes != h.nodes:
        raise ValueError(f"the nodes of g {g.nodes} and the nodes of h {h.nodes} are not the same")

    balloon_groups_g = [[] for _ in h]
    for i_g, balloon_g in enumerate(g):
        # Since h has valid structure at most one h-balloon contains all the nodes of balloon_g
        is_subset = [g.balloon_nodes(i_g) <= h.balloon_nodes(i_h) for i_h in range(len(h))]
        if not any(is_subset):
            return False
        balloon_groups_g[is_subset.index(True)].append(balloon_g)

    return all(
        _poset_le_aux(BalloonGraph(*balloon_group), h[i])
        for i, balloon_group in enumerate(balloon_groups_g)
    )


def poset_eq[T: Hashable](g: BalloonGraph[T], h: BalloonGraph[T]) -> bool:
    """Return whether `g` and `h` are *bi-embeddable*.

    Parameters
    ----------
    g, h : BalloonGraph[T]
        Two balloon graphs on the same set of nodes.

    Returns
    -------
    bool
        Whether both `poset_le(g, h)` and `poset_le(h, g)`.
    """
    return poset_le(g, h) and poset_le(h, g)  # pylint: disable=W1114:arguments-out-of-order
