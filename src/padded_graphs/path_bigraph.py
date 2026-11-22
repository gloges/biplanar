"""Path bi-graphs."""

from typing import Any
from .balloon_graph import BalloonGraph
from .bigraph import BiGraph


class PathBiGraph(BiGraph[int]):
    """A **path bi-graph** is a bi-graph with two groups of nodes, referred to as *east* and *west*.

    The non-negative integers `n_east` and `n_west` give the number of east and west nodes,
    respectively, and the two balloon graphs of the bi-graph must have the nodes
    `{0, 1, ..., n_east + n_west - 1}`; Those less than `n_east` are the *east* nodes and those
    `n_east` or greater are the *west* nodes.
    """

    _n_east: int
    _n_west: int

    def __init__(
        self,
        n_east: int,
        n_west: int,
        g: BalloonGraph[int],
        h: BalloonGraph[int],
        *,
        name: str = '',
        **attr: Any
    ) -> None:
        self._n_east = n_east
        self._n_west = n_west
        super().__init__(g, h, name=name, **attr)
        self._check_balloon_graph_nodes()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Meta
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def n_east(self) -> int:
        """The number of *east* nodes."""
        return self._n_east

    @property
    def n_west(self) -> int:
        """The number of *west* nodes."""
        return self._n_west

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _check_balloon_graph_nodes(self) -> None:
        """Validate the nodes of the two balloon graphs."""
        node_set = set(range(self._n_east + self._n_west))
        for bg in self._balloon_graph:
            if bg.nodes != node_set:
                raise ValueError(f"one of the two balloon graphs does not have nodes {node_set}")

    def check_structure(self) -> None:
        """Validate the structure of the path bi-graph.

        Checks that both balloon graphs have the integer nodes `0, 1, ..., (n_east + n_west - 1)`
        and checks the bi-graph structure (see :meth:`BiGraph.check_structure`).

        Returns quietly if the structure is valid.

        Raises
        -------
        ValueError
            If either of the above conditions is not met (a short message explains the issue).
        """
        self._check_balloon_graph_nodes()
        super().check_structure()
