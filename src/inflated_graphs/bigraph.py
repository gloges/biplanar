"""Bigraphs."""

from collections.abc import Generator, Hashable, Mapping
from itertools import permutations, product
from types import NotImplementedType
from typing import Any, Self
from .balloon_graph import BalloonGraph


class BiGraph[T: Hashable]:
    """A **bi-graph** represents an unordered pair of balloon graphs on a common set of nodes."""

    _name: str
    _attr: dict[str, Any]
    _top: BalloonGraph[T]
    _bot: BalloonGraph[T]
    _node_color: dict[T, Any]

    def __init__(
        self,
        g: BalloonGraph[T],
        h: BalloonGraph[T],
        node_colors: dict[T, Any],
        *,
        name: str = "",
        **attr: Any
    ):
        self._name = name
        self._attr = attr
        self._top = g
        self._bot = h
        self._node_color = node_colors

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
            self._top.copy(),
            self._bot.copy(),
            self._node_color.copy(),
            name=self._name + '-copy' if self._name else '',
            **self._attr.copy()
        )

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graphs and nodes
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def balloon_graphs(self) -> tuple[BalloonGraph[T], BalloonGraph[T]]:
        """The pair of balloon graphs."""
        return self._top, self._bot

    @balloon_graphs.setter
    def balloon_graphs(self, value: tuple[BalloonGraph[T], BalloonGraph[T]]) -> None:
        self._top = value[0]
        self._bot = value[1]

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return self._top.nodes | self._bot.nodes

    @property
    def node_colors(self) -> dict[T, Any]:
        """The colors assigned to the nodes."""
        return self._node_color

    @node_colors.setter
    def node_colors(self, value: Mapping[T, Any]) -> None:
        self._node_color = dict(value)

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
        self._top.relabel_nodes(node_replacements)
        self._bot.relabel_nodes(node_replacements)
        self._node_color = {
            node_replacements.get(n, n): c
            for n, c in self._node_color.items()
            if n in self.nodes
        }

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
        if self._top.nodes != self._bot.nodes:
            raise ValueError("the two graphs do not have the same nodes")

    def _check_node_colors(self) -> None:
        """Validate that all nodes have been assigned a color.

        Returns quietly if all nodes have a color.

        Raises
        ------
        ValueError
            If any node of the graph does not have a color.
        """
        self._node_color = {n: c for n, c in self._node_color.items() if n in self.nodes}
        if self._node_color.keys() != self.nodes:
            raise ValueError(
                f"the nodes {self.nodes - self._node_color.keys()} have not been assigned a color"
            )

    def check_structure(self) -> None:
        """Validate the structure of the bi-graph.

        Checks that...
        - both balloon graphs have the same nodes,
        - all nodes have been assigned a color, and
        - both balloon graphs have valid structure (see :meth:`BalloonGraph.check_structure`).

        Returns quietly if the structure is valid.

        Raises
        ------
        ValueError  
            If any of the above conditions are not met (a short message explains the issue).
        """
        self._check_balloon_graph_nodes()
        self._check_node_colors()
        self._top.check_structure()
        self._bot.check_structure()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   (In)equality
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def __le__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BiGraph):
            return NotImplemented
        return poset_le(self, other)

    def __ge__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BiGraph):
            return NotImplemented
        return poset_le(other, self)

    def __lt__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BiGraph):
            return NotImplemented
        return poset_le(self, other) and not poset_le(other, self)

    def __gt__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BiGraph):
            return NotImplemented
        return poset_le(other, self) and not poset_le(self, other)

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, BiGraph):
            return NotImplemented
        return poset_eq(self, other)


def _value_restricted_permutations[T: Hashable](m: Mapping[T, Hashable]) -> Generator[dict[T, T]]:
    """Yield all permutations of the keys of `m` with the restriction that if `x` is mapped to `y`,
    then `m.get(x) == m.get(y)`.
    """
    keys_by_value = {}
    for key, value in m.items():
        keys_by_value.setdefault(value, []).append(key)
    key_groups = list(keys_by_value.values())

    for key_group_perms in product(*[permutations(group) for group in key_groups]):
        yield {
            x: y
            for group, group_perm in zip(key_groups, key_group_perms)
            for x, y in zip(group, group_perm)
        }


def poset_le[T: Hashable](g: BiGraph[T], h: BiGraph[T]) -> bool:
    """Return whether `g ≤ h`."""
    g.check_structure()
    h.check_structure()

    if g.nodes != h.nodes:
        raise ValueError(f"the nodes of g {g.nodes} and of h {h.nodes} are different")

    if g.node_colors != h.node_colors:
        raise ValueError(f"the node colors for g {g.node_colors} and for h {h.node_colors} differ")

    for node_permutation in _value_restricted_permutations(g.node_colors):
        g_permuted = g.copy()
        g_permuted.balloon_graphs[0].relabel_nodes(node_permutation)
        g_permuted.balloon_graphs[1].relabel_nodes(node_permutation)

        bg_g_0, bg_g_1 = g_permuted.balloon_graphs
        bg_h_0, bg_h_1 = h.balloon_graphs

        if (bg_g_0 <= bg_h_0 and bg_g_1 <= bg_h_1) or (bg_g_1 <= bg_h_0 and bg_g_0 <= bg_h_1):
            return True

    return False


def poset_eq[T: Hashable](g: BiGraph[T], h: BiGraph[T]) -> bool:
    """Return whether both `g ≤ h` and `h ≤ g`."""
    return poset_le(g, h) and poset_le(h, g)  # pylint: disable=W1114:arguments-out-of-order
