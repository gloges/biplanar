"""Bigraphs."""

from __future__ import annotations
from collections.abc import Callable, Collection, Hashable, Mapping, Sequence
from itertools import permutations, product
from typing import Any, Self
from .balloon_graph import BalloonGraph


class BiGraph[T: Hashable]:
    """A **bi-graph** represents an unordered pair of balloon graphs on a common set of nodes."""

    _name: str
    _attr: dict[str, Any]
    _balloon_graph: tuple[BalloonGraph[T], BalloonGraph[T]]

    def __init__(self, g: BalloonGraph[T], h: BalloonGraph[T], *, name: str = "", **attr: Any):
        self._name = name
        self._attr = attr
        self._balloon_graph = g, h

    @classmethod
    def from_data_strings(cls, data_g: str, data_h: str, interpreter: Callable[[str], T]) -> Self:
        """Construct a bi-graph from two balloon graph data strings."""
        return cls(
            BalloonGraph.from_data_string(data_g, interpreter),
            BalloonGraph.from_data_string(data_h, interpreter)
        )

    @classmethod
    def from_data_string(cls, data: str, interpreter: Callable[[str], T]) -> Self:
        """Construct a bi-graph from a string summarizing its two balloon graphs.

        The input string must contain two valid balloon graph data strings formatted as
        `"{balloon_graph_string_0}, {balloon_graph_string_1}"`.

        Parameters
        ----------
        data : str
            String encoding of the bi-graph.
        interpreter : Callable[[str], T]
            A function that converts a node's string representation into a node of type `T`.

        Returns
        -------
        Self
            A bi-graph.

        Raises
        ------
        ValueError
            If there is a parsing error (a short message explains the issue).

        Examples
        --------
        A typical use-case:

        >>> g = BiGraph.from_data_string(
        ...     "{[<0, 1 | A(0, 1)>, <1, 2 | A(1, 2)>]}, {[<0 | >], [<1 | >, <2 | >]}",
        ...     int
        ... )
        >>> g.print_details()
        ╭╼ Balloon graph A
        │  ╭─┬╼ Balloon 0:  nodes = {0, 1, 2}
        │  │ ├─╼  <0, 1 | A(0, 1)>  connected ✓  planar ✓
        │  │ └─╼  <1, 2 | A(1, 2)>  connected ✓  planar ✓
        │  │
        │  ╰╼ Valid structure ✓
        │
        ├╼ Balloon graph B
        │  ╭─┬╼ Balloon 0:  nodes = {0}
        │  │ └─╼  <0 | >  connected ✓  planar ✓
        │  │
        │  ├─┬╼ Balloon 1:  nodes = {1, 2}
        │  │ ├─╼  <1 | >  connected ✓  planar ✓
        │  │ └─╼  <2 | >  connected ✓  planar ✓
        │  │
        │  ╰╼ Valid structure ✓
        │
        ╰╼ Valid structure ✓
        """
        if data[0] != '{' or data[-1] != '}' or data.count('}, {') != 1:
            raise ValueError()
        data_g, data_h = data[1:-1].split('}, {')
        return cls.from_data_strings(data_g, data_h, interpreter)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Meta
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def name(self) -> str:
        """The name of the bi-graph."""
        return self._name

    @name.setter
    def name(self, s: str) -> None:
        self._name = s

    @property
    def attributes(self) -> dict[str, Any]:
        """The attributes of the bi-graph.

        Changes to the returned dictionary modify this bi-graphs's attributes.
        Assigning a mapping replaces the dictionary with a shallow copy of that mapping.
        """
        return self._attr

    @attributes.setter
    def attributes(self, value: Mapping[str, Any]) -> None:
        self._attr = dict(value)

    def copy(self) -> Self:
        """Return a copy of the bi-graph.

        All bi-graph attributes and balloon graph are copied. If the bi-graph
        has a name then '-copy' is appended: otherwise the copy remains unnamed.

        Returns
        -------
        Self
            A copy of the bi-graph.
        """
        return type(self)(
            self._balloon_graph[0].copy(),
            self._balloon_graph[1].copy(),
            name=self._name + '-copy' if self._name else '',
            **self._attr.copy()
        )

    def data_string(self) -> str:
        """Return a string summarizing the two balloon graphs of the bi-graph.

        The data strings of the balloon graphs (see :meth:`BalloonGraph.data_string`)
        are combined as `"{balloon_graph_data_a}, {balloon_graph_data_b}"`.
        Their order is taken to prioritize fewer balloons and anklet graphs first
        and may not match the order of :meth:`BiGraph.balloon_graphs`.

        See Also
        --------
        :meth:`BiGraph.print_details`
        """
        sorted_data = sorted([
            (bg.number_of_balloons(), bg.number_of_anklet_graphs(), bg.data_string())
            for bg in self._balloon_graph
        ])
        return '{' + sorted_data[0][2] + '}, {' + sorted_data[1][2] + '}'

    def print_details(self) -> None:
        """Print detailed information about the bi-graph.

        See Also
        --------
        :meth:`BiGraph.data_string`
        """
        print("╭╼ Balloon graph A")
        self._balloon_graph[0].print_details('│  ')
        print('│')
        print("├╼ Balloon graph B")
        self._balloon_graph[1].print_details('│  ')
        print('│')

        try:
            self.check_structure()
            print("╰╼ Valid structure ✓")
        except ValueError as exc:
            lines = str(exc).split("\n")
            print(f"╰╼ Invalid structure: {lines[0]}")
            for line in lines[1:]:
                print('   ' + line)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graphs and nodes
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def balloon_graphs(self) -> tuple[BalloonGraph[T], BalloonGraph[T]]:
        """The pair of balloon graphs."""
        return self._balloon_graph

    @balloon_graphs.setter
    def balloon_graphs(self, value: tuple[BalloonGraph[T], BalloonGraph[T]]) -> None:
        self._balloon_graph = value

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return self._balloon_graph[0].nodes | self._balloon_graph[1].nodes

    def relabel_nodes(self, node_replacements: Mapping[T, T], /) -> None:
        """Relabel nodes in the two balloon graphs simultaneously.

        Parameters
        ----------
        node_replacements : Mapping[T, T]
            Mapping from existing nodes to their replacements. Nodes not present as keys
            are left unaltered, and keys that are not nodes of this bi-graph are ignored.

        Raises
        ------
        ValueError
            If the two balloon graphs do not have the same nodes
            or if the node replacements would lead to a collision.
        """
        self._check_balloon_graph_nodes()
        self._balloon_graph[0].relabel_nodes(node_replacements)
        self._balloon_graph[1].relabel_nodes(node_replacements)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _check_balloon_graph_nodes(self) -> None:
        """Validate that the two balloon graphs have the same nodes.

        Returns quietly if they have the same nodes.

        Raises
        ------
        ValueError
            If the nodes in the two balloon graphs are different.
        """
        if self._balloon_graph[0].nodes != self._balloon_graph[1].nodes:
            raise ValueError("the two graphs do not have the same nodes")

    def check_structure(self) -> None:
        """Validate the structure of the bi-graph.

        Checks that the balloon graphs have the same nodes
        and that both have valid structure (see :meth:`BalloonGraph.check_structure`).

        Returns quietly if the structure is valid.

        Raises
        ------
        ValueError  
            If either of the above conditions is not met (a short message explains the issue).
        """
        self._check_balloon_graph_nodes()
        self._balloon_graph[0].check_structure()
        self._balloon_graph[1].check_structure()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graph operations
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def merge_nodes(self, u: T, v: T, /) -> list[BiGraph[T]]:
        self.check_structure()

        results = {}
        for g, h in product(
            self._balloon_graph[0].merge_nodes(u, v),
            self._balloon_graph[1].merge_nodes(u, v)
        ):
            big = BiGraph(g, h)
            results[big.data_string()] = big

        return list(results.values())

# ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==
#   (In)equality
# ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==


def poset_le[T: Hashable](
    g: BiGraph[T],
    h: BiGraph[T],
    node_groups: Sequence[Collection[T]]
) -> bool:
    """Return whether `g ≤ h`."""
    g.check_structure()
    h.check_structure()

    if g.nodes != h.nodes:
        raise ValueError(f"the nodes of g {g.nodes} and of h {h.nodes} are different")

    node_group_union = set().union(*[set(group) for group in node_groups])

    if sum(len(group) for group in node_groups) != len(node_group_union):
        raise ValueError(f"the sets in {node_groups!r} are not disjoint")

    if node_group_union != g.nodes:
        raise ValueError(
            f"nodes in node_groups {node_groups}\ndo not exactly match the graphs' nodes {g.nodes}"
        )

    for node_group_permutations in product(*[permutations(group) for group in node_groups]):
        node_permutation = {
            u: v
            for group, group_perm in zip(node_groups, node_group_permutations)
            for u, v in zip(group, group_perm)
        }

        g_permuted = g.copy()
        g_permuted.balloon_graphs[0].relabel_nodes(node_permutation)
        g_permuted.balloon_graphs[1].relabel_nodes(node_permutation)

        bg_g_0, bg_g_1 = g_permuted.balloon_graphs
        bg_h_0, bg_h_1 = h.balloon_graphs

        if (bg_g_0 <= bg_h_0 and bg_g_1 <= bg_h_1) or (bg_g_1 <= bg_h_0 and bg_g_0 <= bg_h_1):
            return True

    return False


def poset_eq[T: Hashable](
    g: BiGraph[T],
    h: BiGraph[T],
    node_groups: Sequence[Collection[T]]
) -> bool:
    """Return whether both `g ≤ h` and `h ≤ g`."""
    # pylint: disable=W1114:arguments-out-of-order
    return poset_le(g, h, node_groups) and poset_le(h, g, node_groups)
