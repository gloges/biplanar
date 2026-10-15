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
        """Return the number of nodes. Use: `len(g)`.

        See Also
        --------
        :meth:`number_of_nodes` : identical method
        """
        return len(self._node)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Nodes
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def nodes(self) -> set[T]:
        """The set of nodes."""
        return set(self._node)

    def number_of_nodes(self) -> int:
        """Return the number of nodes.

        See Also
        --------
        :meth:`__len__` : identical method
        """
        return len(self._node)

    def add_node(self, n: T) -> None:
        """Add a node."""
        raise NotImplementedError()

    def remove_node(self, n: T) -> None:
        """Remove a node."""
        raise NotImplementedError()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Hyperedges
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def number_of_hyperedges(self) -> int:
        """Return the number of hyperedges (counted with multiplicity).

        See Also
        --------
        :meth:`number_of_unique_hyperedges`
        """
        return len(self._edge)

    def number_of_unique_hyperedges(self) -> int:
        """Return the number of unique hyperedges (i.e. counted without multiplicity).

        See Also
        --------
        :meth:`number_of_hyperedges`
        """
        return sum(self._edge.values())

    def add_hyperedge(self, hype: Anklet[T], k: int = 1) -> None:
        """Add a hyperedge."""
        raise NotImplementedError()

    def remove_hyperedge(self, hype: Anklet[T], k: int = 1) -> None:
        """Remove a hyperedge."""
        raise NotImplementedError()
