"""Balloon graphs."""

from collections.abc import Hashable
from ankletgraph import AnkletGraph


class BalloonGraph[T: Hashable]:
    """A **balloon graph** represents an equivalence class of inflated graph embeddings."""

    _name: str
    _component: list[AnkletGraph[T]]

    def __init__(self, *, name: str = "") -> None:
        self._name = name
        self._component = []

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

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Components
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def add_component(self, g: AnkletGraph[T]) -> None:
        """Add a graph component."""
        raise NotImplementedError()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def check_structure(self) -> None:
        """Validate the structure of the balloon graph."""
        # Form the meta-graph whose meta-nodes are the nodes and components of the balloon graph
        # and with meta-edges when a node is contained in a component.
        # This bipartite graph must be acyclic.
        # All components must also have a 'balloon' attribute
        # and it must be the same for components which share a node.
        raise NotImplementedError()
