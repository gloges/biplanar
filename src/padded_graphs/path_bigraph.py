"""Path bi-graphs."""

from collections.abc import Generator
from itertools import permutations, product
from types import NotImplementedType
from typing import Any, Literal, Self
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

    @property
    def nodes_east(self) -> set[int]:
        """The set of *east* nodes."""
        return set(range(self._n_east))

    @property
    def nodes_west(self) -> set[int]:
        """The set of *west* nodes."""
        return set(range(self._n_east, self._n_east + self._n_west))

    def copy(self) -> Self:
        """Return a copy of the path bi-graph.

        All path bi-graph attributes and balloon graphs are copied. If the path bi-graph
        has a name then '-copy' is appended: otherwise the copy remains unnamed.

        Returns
        -------
        Self
            A copy of the path bi-graph.
        """
        return type(self)(
            self._n_east,
            self._n_west,
            self._balloon_graph[0].copy(),
            self._balloon_graph[1].copy(),
            name=self._name + '-copy' if self._name else '',
            **self._attr.copy()
        )

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

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Node permutation
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def node_permutations(
        self,
        *,
        which: Literal["east", "west", "both"] = "both"
    ) -> Generator[Self]:
        """Yield copies of the path bi-graph with east/west nodes permuted amongst themselves.

        If `which == "east"` returns `n_east!` permuted copies,
        if `which == "west"` returns `n_west!` permuted copies, and
        if `which == "both"` returns `n_east! * n_west!` permuted copies.
        In each case some of the returned path bi-graphs may be duplicates.
        """
        east_perms = (
            permutations(self.nodes_east)
            if which in ("east", "both")
            else [self.nodes_east]
        )
        west_perms = (
            permutations(self.nodes_west)
            if which in ("west", "both")
            else [self.nodes_west]
        )
        for east_west_perms in product(east_perms, west_perms):
            node_permutation = {
                u: v
                for group, group_perm in zip([self.nodes_east, self.nodes_west], east_west_perms)
                for u, v in zip(group, group_perm)
            }
            g_permuted = self.copy()
            g_permuted.balloon_graphs[0].relabel_nodes(node_permutation)
            g_permuted.balloon_graphs[1].relabel_nodes(node_permutation)
            yield g_permuted

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   (In)equality
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def __le__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, PathBiGraph):
            return NotImplemented
        return poset_le(self, other)

    def __ge__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, PathBiGraph):
            return NotImplemented
        return poset_le(other, self)

    def __lt__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, PathBiGraph):
            return NotImplemented
        return poset_le(self, other) and not poset_le(other, self)

    def __gt__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, PathBiGraph):
            return NotImplemented
        return poset_le(other, self) and not poset_le(self, other)

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, PathBiGraph):
            return NotImplemented
        return poset_eq(self, other)


def poset_le(g: PathBiGraph, h: PathBiGraph) -> bool:
    """Return whether `g ≤ h`.

    The path bi-graph `g` is *less than or equal to* the path bi-graph `h` *if and only if*
    there exist permutations of the east and west nodes of `g` such that each balloon graph
    of `g` with permuted nodes is less than or equal to a different balloon graph of `h`.

    Parameters
    ----------
    g, h : PathBiGraph
        Two path bi-graphs to be compared.

    Returns
    -------
    bool
        Whether `g ≤ h`, as described above.

    Raises
    ------
    ValueError
        If the numbers of east and west nodes of `g` and `h` are not the same.
    """
    if (g.n_east, g.n_west) != (h.n_east, h.n_west):
        raise ValueError(
            f"nodes do not match: ({g.n_east}, {g.n_west}) != ({h.n_east}, {h.n_west})"
        )
    g.check_structure()
    h.check_structure()

    for g_permuted in g.node_permutations():
        bg_g_0, bg_g_1 = g_permuted.balloon_graphs
        bg_h_0, bg_h_1 = h.balloon_graphs
        if (bg_g_0 <= bg_h_0 and bg_g_1 <= bg_h_1) or (bg_g_1 <= bg_h_0 and bg_g_0 <= bg_h_1):
            return True
    return False


def poset_eq(g: PathBiGraph, h: PathBiGraph) -> bool:
    """Return whether both `g ≤ h` and `h ≤ g`."""
    return poset_le(g, h) and poset_le(h, g)  # pylint: disable=W1114:arguments-out-of-order
