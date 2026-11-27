"""Path bi-graphs."""

from collections.abc import Generator
from itertools import permutations, product
from types import NotImplementedType
from typing import Any, Literal, Self
from .balloon_graph import BalloonGraph
from .bigraph import BiGraph


class PathBiGraph(BiGraph[int]):
    """A **path bi-graph** is a bi-graph with three groups of nodes,
    referred to as *left*, *center* and *right*.

    The non-negative integers `n_left`, `n_center` and `n_right` give the number
    of left, center and right nodes, respectively, and the two balloon graphs
    of the bi-graph must have the nodes `{0, 1, ..., n_left + n_center + n_right - 1}`;
    the first `n_left` are *left*nodes, the next `n_center` are *center* nodes and the last
    `n_right` are *right* nodes.
    """

    _n_left: int
    _n_center: int
    _n_right: int

    def __init__(
        self,
        n_left: int,
        n_center: int,
        n_right: int,
        g_data: BalloonGraph[int] | str,
        h_data: BalloonGraph[int] | str,
        *,
        name: str = '',
        **attr: Any
    ) -> None:
        self.n_left = n_left
        self.n_center = n_center
        self.n_right = n_right
        super().__init__(
            BalloonGraph.from_data_string(g_data, int) if isinstance(g_data, str) else g_data,
            BalloonGraph.from_data_string(h_data, int) if isinstance(h_data, str) else h_data,
            name=name,
            **attr
        )
        self._check_left_center_right_nodes()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Meta
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def n_left(self) -> int:
        """The number of *left* nodes."""
        return self._n_left

    @n_left.setter
    def n_left(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("n_left must be a non-negative integer")
        self._n_left = value

    @property
    def n_center(self) -> int:
        """The number of *center* nodes."""
        return self._n_center

    @n_center.setter
    def n_center(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("n_center must be a non-negative integer")
        self._n_center = value

    @property
    def n_right(self) -> int:
        """The number of *right* nodes."""
        return self._n_right

    @n_right.setter
    def n_right(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("n_right must be a non-negative integer")
        self._n_right = value

    @property
    def n_total(self) -> int:
        """The total number of *left*, *center* and *right* nodes."""
        return self._n_left + self._n_center + self._n_right

    @property
    def nodes_left(self) -> set[int]:
        """The set of *left* nodes."""
        return set(range(self._n_left))

    @property
    def nodes_center(self) -> set[int]:
        """The set of *center* nodes."""
        return set(range(self._n_left, self._n_left + self._n_center))

    @property
    def nodes_right(self) -> set[int]:
        """The set of *right* nodes."""
        return set(
            range(self._n_left + self._n_center, self._n_left + self._n_center + self._n_right)
        )

    @property
    def nodes(self) -> set[int]:
        """The set of *left*, *center* and *right* nodes."""
        return set(range(self._n_left + self._n_center + self._n_right))

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
            self._n_left,
            self._n_center,
            self._n_right,
            self._balloon_graph[0].copy(),
            self._balloon_graph[1].copy(),
            name=self._name + '-copy' if self._name else '',
            **self._attr.copy()
        )

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Structure
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def _check_left_center_right_nodes(self) -> None:
        """Validate the nodes of the two balloon graphs."""
        for bg in self._balloon_graph:
            if bg.nodes != self.nodes:
                raise ValueError(f"one of the two balloon graphs does not have nodes {self.nodes}")

    def check_structure(self) -> None:
        """Validate the structure of the path bi-graph.

        Checks that both balloon graphs have the integer nodes `0, 1, ..., (n_total - 1)`
        and checks the bi-graph structure (see :meth:`BiGraph.check_structure`).

        Returns quietly if the structure is valid.

        Raises
        -------
        ValueError
            If either of the above conditions is not met (a short message explains the issue).
        """
        self._check_left_center_right_nodes()
        super().check_structure()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graph operations
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def reverse(self) -> Self:
        """Swap left and right nodes."""
        bgraph_0 = self._balloon_graph[0].copy()
        bgraph_1 = self._balloon_graph[1].copy()
        mapping = {i: self.n_total - i - 1 for i in range(self.n_total)}
        bgraph_0.relabel_nodes(mapping)
        bgraph_1.relabel_nodes(mapping)
        return type(self)(self.n_right, self.n_center, self.n_left, bgraph_0, bgraph_1)

    def node_permutations(
        self,
        *,
        which: Literal["left", "right", "both"] = "both"
    ) -> Generator[Self]:
        """Yield copies of the path bi-graph with left/right nodes permuted amongst themselves.

        If `which == "left"` returns `n_left!` permuted copies,
        if `which == "right"` returns `n_right!` permuted copies, and
        if `which == "both"` returns `n_left! * n_right!` permuted copies.
        In each case some of the returned path bi-graphs may be duplicates.
        """
        left_perms = (
            permutations(self.nodes_left)
            if which in ("left", "both")
            else [self.nodes_left]
        )
        right_perms = (
            permutations(self.nodes_right)
            if which in ("right", "both")
            else [self.nodes_right]
        )
        for left_right_perms in product(left_perms, right_perms):
            node_permutation = {
                u: v
                for group, group_perm in zip([self.nodes_left, self.nodes_right], left_right_perms)
                for u, v in zip(group, group_perm)
            }
            g_permuted = self.copy()
            g_permuted.balloon_graphs[0].relabel_nodes(node_permutation)
            g_permuted.balloon_graphs[1].relabel_nodes(node_permutation)
            yield g_permuted

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Closability
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def closable(self) -> bool:
        """Determine if the path bi-graph can be closed into a cycle.

        For this to a meaningful notion the number of left and right nodes must be equal.
        """
        if self._n_left != self._n_right:
            raise ValueError(f"n_left = {self._n_left} != {self._n_right} = n_right")
        return len(self.join_node_subsets(self.nodes_left, self.nodes_right)) > 0

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
    there exist permutations of the left and right nodes of `g` such that each balloon graph
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
        If either `g` or `h` has center nodes or
        ff the numbers of left and right nodes of `g` and `h` are not the same.
    """
    if g.n_center != 0 or h.n_center != 0:
        raise ValueError("cannot compare path bi-graphs if n_center is non-zero.")
    if (g.n_left, g.n_right) != (h.n_left, h.n_right):
        raise ValueError(
            f"left/right nodes do not match: ({g.n_left}, {g.n_right}) != ({h.n_left}, {h.n_right})"
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


# ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==
#   Joining
# ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==


def join(g: PathBiGraph, h: PathBiGraph) -> list[PathBiGraph]:
    """Join two path bi-graphs.

    The right nodes of `g` are joined to the left nodes of `h` in all possible ways to form
    path bi-graphs with `g.n_left` left nodes and `h.n_right` right nodes.
    The number of right nodes in `g` must be the same as the number of left nodes in `h`.

    Parameters
    ----------
    g, h : PathBiGraph
        Two path bi-graphs with `g.n_right == h.n_left`.

    Returns
    -------
    list[PathBiGraph]
        Path bi-graphs with `g.n_left` left nodes and `h.n_right` right nodes.

    Raises
    ------
    ValueError
        If either `g` or `h` have center nodes or
        if `g.n_right != h.n_left` or if either of `g` or `h` does not have valid structure.
    """
    if g.n_center != 0 or h.n_center != 0:
        raise ValueError("cannot join if n_center is non-zero")
    if g.n_right != h.n_left:
        raise ValueError(f"g.n_right = {g.n_right} != {h.n_left} = h.n_left")

    g.check_structure()
    h.check_structure()

    g_right_mapping = {i: i + h.n_right for i in g.nodes_right}
    h_left_mapping = {i: i + g.n_left + h.n_right + g.n_right for i in h.nodes_left}
    h_mapping = {i: i - h.n_left + g.n_left for i in h.nodes_right}
    h_mapping.update(h_left_mapping)

    h_relabeled = h.copy()
    h_relabeled.relabel_nodes(h_mapping)

    results = {}
    for g_permuted in g.node_permutations(which='right'):
        g_permuted.relabel_nodes(g_right_mapping)
        gh = BiGraph(
            BalloonGraph(*g_permuted.balloon_graphs[0], *h_relabeled.balloon_graphs[1]),
            BalloonGraph(*g_permuted.balloon_graphs[1], *h_relabeled.balloon_graphs[0])
        )
        for big in gh.join_node_subsets(g_right_mapping.values(), h_left_mapping.values()):
            pbg = PathBiGraph(g.n_left, 0, h.n_right, *big.balloon_graphs)
            results[pbg.data_string()] = pbg

        gh = BiGraph(
            BalloonGraph(*g_permuted.balloon_graphs[0], *h_relabeled.balloon_graphs[0]),
            BalloonGraph(*g_permuted.balloon_graphs[1], *h_relabeled.balloon_graphs[1])
        )
        for big in gh.join_node_subsets(g_right_mapping.values(), h_left_mapping.values()):
            pbg = PathBiGraph(g.n_left, 0, h.n_right, *big.balloon_graphs)
            results[pbg.data_string()] = pbg

    return list(results.values())
