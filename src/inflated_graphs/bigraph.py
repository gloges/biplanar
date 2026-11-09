"""Bigraphs."""

from collections.abc import Hashable, Mapping
from typing import Any
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

