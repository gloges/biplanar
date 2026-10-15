"""Anklet graphs."""

from collections.abc import Hashable, Iterator
from typing import Any
from anklet import Anklet


class AnkletGraph[T: Hashable]:
    """An **anklet graph** is a multi-hypergraph with additional combinatorial structure."""

    _name: str
    _node: dict[T, dict[str, Any]]
    _edge: dict[Anklet[T], int]

    def __init__(self, *, name: str = "") -> None:
        self._name = name
        self._node = {}
        self._edge = {}

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

    def __iter__(self) -> Iterator[T]:
        """Iterate over the nodes. Use: `for n in g`."""
        return iter(self._node)

    def __contains__(self, n: T) -> bool:
        """Return whether `n` is a node in the graph. Use: `n in g`."""
        try:
            return n in self._node
        except TypeError:
            return False

    def __len__(self) -> int:
        """Return the number of nodes. Use: `len(g)`."""
        return len(self._node)
