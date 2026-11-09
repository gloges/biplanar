"""Bigraphs."""

from collections.abc import Hashable
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
