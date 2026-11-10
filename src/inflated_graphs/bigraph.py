"""Bigraphs."""

from collections.abc import Hashable, Mapping
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
