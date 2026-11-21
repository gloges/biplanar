"""Combinatorial anklets."""

from collections.abc import (
    Callable,
    Collection,
    Container,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence
)
from itertools import combinations, permutations, product
from types import NotImplementedType
from typing import Any, Self
import networkx as nx


class Anklet[T](tuple[T, ...]):
    """An **anklet** is a combinatorial bracelet with all beads distinct.

    Anklets are tuples with a weaker notion of equality, where two anklets are *equal*
    if one can be obtained from the other by cyclic rotation and reversal.
    Equivalently, an anklet with `n` beads is an *equivalence class* of tuples given
    by the orbit of its defining `n`-tuple under the group action of `Dihₙ`.

    An anklet with `n` beads can be thought of as a labeled `n`-cycle graph or an `n`-gon
    with labeled vertices.

    ### Partial order

    There is a natural partial order on anklets where `a ≤ b` *if and only if*
    `a` can be obtained from `b` by removing beads. With this partial order,
    the set of anklets is a *partially ordered set* with the empty anklet for its least element.

    Examples
    --------
    The beads of an anklet must be distinct:

    >>> Anklet(0, 1, 2, 1)
    Traceback (most recent call last):
    ...
    ValueError: the beads (0, 1, 2, 1) are not distinct

    Anklets with different defining tuples are equal *if and only if*
    one can be obtained from the other by cyclic rotation and reversal:

    >>> Anklet(0, 1, 2, 3) == Anklet(1, 2, 3, 0)
    True
    >>> Anklet(0, 1, 2, 3) == Anklet(2, 3, 0, 1)
    True
    >>> Anklet(0, 1, 2, 3) == Anklet(2, 1, 0, 3)
    True
    >>> Anklet(0, 1, 2, 3) == Anklet(0, 1, 3, 2)
    False

    The partial order:

    >>> Anklet() <= Anklet(1) <= Anklet(1, 2, 5) <= Anklet(3, 5, 1, 2) <= Anklet(0, 1, 2, 3, 4, 5)
    True
    >>> Anklet() <= Anklet(0, 2) <= Anklet(0, 2, 3) <= Anklet(0, 4, 3, 2) <= Anklet(0, 1, 2, 3, 4)
    True
    >>> Anklet(0, 1, 3, 2) <= Anklet(0, 1, 2, 3, 4)
    False
    >>> Anklet(2) <= Anklet(0, 1, 3)
    False

    Note that comparing against a tuple reverts to `tuple.__le__`
    using the defining tuple of the anklet:

    >>> Anklet(0, 1, 2) <= (1, 2, 3, 4)  # !!
    True
    >>> (0, 2, 1) <= Anklet(0, 1, 2)  # !!
    False
    """

    def __new__(cls, *beads: T) -> Self:
        if len(set(beads)) != len(beads):
            raise ValueError(f"the beads {beads} are not distinct")
        return super().__new__(cls, beads)

    @classmethod
    def from_iterable(cls, beads: Iterable[T], /) -> Self:
        """Construct an anklet from a finite sequence of beads.

        Unlike `Anklet(x)`, this method treats `x` as a source of beads
        rather than as the lone bead of the anklet.

        Parameters
        ----------
        beads : Iterable[T]
            A finite sequence of distinct beads.

        Returns
        -------
        Self
            An anklet with the given beads.

        Raises
        ------
        ValueError
            If the beads are not distinct.

        Examples
        --------
        >>> Anklet.from_iterable(range(4)) == Anklet(0, 1, 2, 3)
        True
        """
        return cls(*beads)

    def __repr__(self) -> str:
        return "A(" + ", ".join(repr(bead) for bead in self) + ")"

    def __add__(self, value: object) -> NotImplementedType:
        return NotImplemented

    def __mul__(self, value: object) -> NotImplementedType:
        return NotImplemented

    def __rmul__(self, value: object) -> NotImplementedType:
        return NotImplemented

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Removing/replacing beads
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def without_bead(self, bead_to_remove: T, /) -> Self:
        """Return the sub-anklet formed by removing a bead.

        The relative order of all retained beads is preserved.

        Parameters
        ----------
        bead_to_remove : T
            A bead to remove from the anklet.

        Returns
        -------
        Self
            The anklet with `bead_to_remove` removed, if present.

        See Also
        --------
        :meth:`Anklet.without_beads`,
        :meth:`Anklet.restrict_beads`,
        :meth:`Anklet.replace_beads`

        Examples
        --------
        >>> a = Anklet(5, 2, 3, 0, 4, 1)
        >>> a.without_bead(3)
        A(5, 2, 0, 4, 1)
        >>> a.without_bead(6)
        A(5, 2, 3, 0, 4, 1)
        """
        return type(self).from_iterable(b for b in self if b is not bead_to_remove)

    def without_beads(self, beads_to_remove: Container[T], /) -> Self:
        """Return the sub-anklet formed by removing beads.

        The relative order of all retained beads is preserved.

        Parameters
        ----------
        beads_to_remove : Container[T]
            Beads to remove from the anklet.

        Returns
        -------
        Self
            Anklet with beads from `beads_to_remove` removed, if present.

        See Also
        --------
        :meth:`Anklet.without_bead`,
        :meth:`Anklet.restrict_beads`,
        :meth:`Anklet.replace_beads`

        Examples
        --------
        >>> Anklet(5, 2, 3, 0, 4, 1).without_beads((0, 2))
        A(5, 3, 4, 1)
        >>> Anklet(5, 2, 3, 0, 4, 1).without_beads(Anklet(0, 1, 6))
        A(5, 2, 3, 4)
        """
        return type(self).from_iterable(b for b in self if b not in beads_to_remove)

    def restrict_beads(self, beads_to_keep: Container[T], /) -> Self:
        """Return the sub-anklet formed by restricting to a subset of the beads.

        The relative order of all retained beads is preserved.

        Parameters
        ----------
        beads_to_keep : Container[T]
            Beads to *not* remove from the anklet.

        Returns
        -------
        Self
            Anklet with all beads not in `beads_to_keep` removed.

        See Also
        --------
        :meth:`Anklet.without_bead`,
        :meth:`Anklet.without_beads`,
        :meth:`Anklet.replace_beads`

        Examples
        --------
        >>> Anklet(5, 2, 3, 0, 4, 1).restrict_beads(range(3))
        A(2, 0, 1)
        >>> Anklet(5, 2, 3, 0, 4, 1).restrict_beads(Anklet(0, 1, 4, 6))
        A(0, 4, 1)
        """
        return type(self).from_iterable(b for b in self if b in beads_to_keep)

    def replace_beads(self, bead_replacements: Mapping[T, T], /) -> Self:
        """Return a new anklet with the specified beads replaced.

        Parameters
        ----------
        bead_replacements : Mapping[T, T]
            Mapping from existing beads to their replacements. Beads not present as keys
            are left unaltered, and keys that are not beads of this anklet are ignored.

        Returns
        -------
        Self
            Anklet with the specified replacements applied.

        Raises
        ------
        ValueError
            If the resulting beads are not distinct.

        See Also
        --------
        :meth:`Anklet.without_bead`,
        :meth:`Anklet.without_beads`,
        :meth:`Anklet.restrict_beads`

        Examples
        --------
        >>> Anklet.from_iterable(range(6)).replace_beads({3: 7, 8: 0})
        A(0, 1, 2, 7, 4, 5)
        >>> Anklet.from_iterable(range(6)).replace_beads({1: 2, 2: 1, 3: 5, 4: 6, 5: 4})
        A(0, 2, 1, 5, 6, 4)
        >>> Anklet.from_iterable(range(6)).replace_beads({0: 5})
        Traceback (most recent call last):
        ...
        ValueError: the beads (5, 1, 2, 3, 4, 5) are not distinct
        >>> Anklet.from_iterable(range(6)).replace_beads({0: 7, 3: 7})
        Traceback (most recent call last):
        ...
        ValueError: the beads (7, 1, 2, 7, 4, 5) are not distinct
        """
        return type(self).from_iterable(bead_replacements.get(b, b) for b in self)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   (In)equality
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def representatives(self) -> Iterator[tuple[T, ...]]:
        """Generate all representative tuples of the anklet.

        For an anklet of length `n ≥ 3`, this yields the `2n` images
        of its defining tuple under the action of `Dihₙ`.
        Anklets of length `n ≤ 1` and `n = 2` yield only one and two representatives, respectively,
        since in these cases cyclic rotation and reversal are not distinct operations.

        Yields
        ------
        tuple[T, ...]
            A representative tuple of the anklet, equivalent to the defining tuple
            up to cyclic permutation and reversal.

        Examples
        --------
        >>> list(Anklet().representatives())
        [()]
        >>> list(Anklet(0).representatives())
        [(0,)]
        >>> list(Anklet(0, 1).representatives())
        [(0, 1), (1, 0)]
        >>> list(Anklet(0, 1, 2).representatives())
        [(0, 1, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0), (1, 0, 2), (0, 2, 1)]
        >>> len(list(Anklet.from_iterable(range(100)).representatives()))
        200
        """
        if len(self) <= 1:
            yield tuple(self)
            return
        if len(self) == 2:
            yield tuple(self)
            yield tuple(reversed(self))
            return
        for vals in (self, self[::-1]):
            for i in range(len(self)):
                yield vals[i:] + vals[:i]

    def __hash__(self) -> int:
        return hash(frozenset(self.representatives()))

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, Anklet):
            return NotImplemented
        return self in other.representatives()

    def __le__(self, other: object) -> NotImplementedType | bool:
        """Return whether the anklet is a *sub-anklet* of `other`.

        An anklet `a` is a sub-anklet of another anklet `b` (*i.e.* `a <= b`)
        if the beads of `a` appear in the prescribed cyclic order as a subsequence of `b`.
        Equivalently, `a <= b` means that it is possible to delete beads from `b` to produce `a`.

        Parameters
        ----------
        other : object
            An anklet.

        Returns
        -------
        NotImplementedType or bool
            `NotImplemented` if `other` is not an anklet.
            Otherwise, whether this anklet is a sub-anklet of `other`.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return self == other.restrict_beads(self)

    def __lt__(self, other: object) -> NotImplementedType | bool:
        """Return whether `self <= other` and `self != other`.

        See :meth:`Anklet.__le__` for the definition of the underlying partial order on anklets.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return len(self) < len(other) and self <= other

    def __ge__(self, other: object) -> NotImplementedType | bool:
        """Return whether `other <= self`.

        See :meth:`Anklet.__le__` for the definition of the underlying partial order on anklets.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return other <= self

    def __gt__(self, other: object) -> NotImplementedType | bool:
        """Return whether `other <= self` and `self != other`.

        See :meth:`Anklet.__le__` for the definition of the underlying partial order on anklets.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return len(other) < len(self) and other <= self

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Other
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def standardized(self, bead_key: Callable[[T], Any] | None = None) -> Self:
        """Return an equivalent anklet with minimal defining tuple.

        Parameters
        ----------
        bead_key : Callable[[T], Any] or None, optional (default=None)
            Function mapping beads to orderable keys. If None, compare beads directly.

        Returns
        -------
        Self
            An equivalent anklet.

        Raises
        ------
        TypeError
            If `<` is not supported between beads.

        Examples
        --------
        >>> Anklet(2, 0, 1).standardized()
        A(0, 1, 2)
        >>> Anklet(2, 1, 0, 3).standardized()
        A(0, 1, 2, 3)
        >>> Anklet(1+0j, 1j).standardized()
        Traceback (most recent call last):
        ...
        TypeError: '<' not supported between instances of 'complex' and 'complex'
        >>> Anklet(1+0j, 1j).standardized(lambda z: (z.real, z.imag))
        A(1j, (1+0j))
        """
        return type(self).from_iterable(
            min(
                self.representatives(),
                key=None if bead_key is None else lambda t: tuple(map(bead_key, t))
            )
        )

    def to_wheel_graph(self) -> nx.Graph:
        """Return a wheel graph representation of the anklet.

        An anklet with `n` beads is represented by the wheel graph `Wₙ` on the nodes `0, 1, ..., n`;
        the node `0` is the central 'hub' and the nodes `1, 2, ..., n` form the outer `n`-cycle.
        Note that for `n = 1` and `n = 2` the graph degenerates and has fewer than `2n` edges.

        The nodes in the `n`-cycle have an 'anklet' attribute with values
        the corresponding beads of the anklet.

        Returns
        -------
        networkx.Graph
            A wheel graph with nodes labeled by the anklet.

        Examples
        --------
        >>> g = Anklet.from_iterable('abcd').to_wheel_graph()
        >>> sorted(g.nodes)
        [0, 1, 2, 3, 4]
        >>> sorted(g.edges)
        [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
        >>> nx.get_node_attributes(g, 'anklet')
        {1: 'a', 2: 'b', 3: 'c', 4: 'd'}

        For `n = 1` and `n = 2` beads the wheel graph degenerates and has fewer than `2n` edges:

        >>> for n in range(5):
        ...     print(f'{n} beads:', Anklet.from_iterable(range(n)).to_wheel_graph())
        0 beads: Graph with 1 nodes and 0 edges
        1 beads: Graph with 2 nodes and 1 edges
        2 beads: Graph with 3 nodes and 3 edges
        3 beads: Graph with 4 nodes and 6 edges
        4 beads: Graph with 5 nodes and 8 edges
        """
        g = nx.wheel_graph(len(self) + 1)
        nx.set_node_attributes(g, dict(enumerate(self, start=1)), 'anklet')
        return g

    def noncrossing(self, x: Collection[T], y: Collection[T]) -> bool:
        """Return whether two collections of beads in the anklet are non-crossing.

        Returns `False` if the anklet does not contain all elements from both `x` and `y`.

        Otherwise, consider arranging the beads of the anklet on the boundary of a disk
        in the prescribed cyclic order and joining the elements of `x` and `y` into sub-anklets
        via a series of chords. Return `True` if the *interiors* of the two chord cycles
        are disjoint and `False` if they intersect.

        Note that `x` and `y` need not be disjoint;
        their corresponding sub-anklets may meet at up to two points without forcing a crossing.

        Parameters
        ----------
        x, y : Collection[T]
            Two sets of beads.

        Returns
        -------
        bool
            Whether `x` and `y` are non-crossing subsets of beads in the anklet.

        Examples
        --------
        >>> a = Anklet.from_iterable(range(6))

        A triangle and digon which are disjoint:

        >>> a.noncrossing({0, 1, 2}, {3, 4})
        True

        Two triangles which meet at a vertex:

        >>> a.noncrossing([0, 1, 2], {2, 3, 4})
        True

        Two triangles which meet at two vertices:

        >>> a.noncrossing((0, 2, 5), {2, 3, 5})
        True

        Two triangles which cross:

        >>> a.noncrossing(Anklet(0, 1, 4), {2, 3, 5})
        False

        Two coincident triangles:

        >>> a.noncrossing({0, 1, 2}, {0, 1, 2})
        False
        """
        if not set(x) <= set(self) or not set(y) <= set(self):
            # The anklet does not contain all of the elements of both 'x' and 'y'
            return False

        # Form the disjoint union of three labeled wheel graphs,
        # one for the parent anklet and one each for the sub-anklets corresponding to 'x' and 'y'
        g = nx.disjoint_union_all(
            a.to_wheel_graph() for a in [self, self.restrict_beads(x), self.restrict_beads(y)]
        )

        # Join by an edge all pairs of nodes which share a bead label
        label_groups = {}
        for n, label in nx.get_node_attributes(g, 'anklet').items():
            label_groups.setdefault(label, set()).add(n)

        for node_group in label_groups.values():
            for u, v in combinations(node_group, 2):
                g.add_edge(u, v)

        return nx.is_planar(g)

    def cut(self, *beads_to_cut: T) -> list[tuple[T, ...]]:
        """Cut the anklet at the given beads into a number of subsequences.

        The relative order and orientation of the sequences is preserved.

        Parameters
        ----------
        beads_to_cut : Collection[T]
            Set of beads at which to cut the anklet.

        Returns
        -------
        list[tuple[T, ...]]
            The sequences of beads between the cuts.

        Raises
        ------
        ValueError
            If the anklet does not contain any of the beads from `beads_to_cut`.

        Examples
        --------
        >>> Anklet.from_iterable(range(8)).cut(2)
        [(3, 4, 5, 6, 7, 0, 1)]
        >>> Anklet.from_iterable(range(8)).cut(2, 5)
        [(3, 4), (6, 7, 0, 1)]
        >>> Anklet.from_iterable(range(8)).cut(1, 6, 4, 'a')
        [(2, 3), (5,), (7, 0)]
        >>> Anklet.from_iterable(range(8)).cut(0, 1, 4, 5)
        [(), (2, 3), (), (6, 7)]
        """
        indices = [i for i, b in enumerate(self) if b in beads_to_cut]
        if not indices:
            raise ValueError(f"{self} does not contain any of the beads in {beads_to_cut}")
        indices.append(indices[0] + len(self))
        double_cover = 2 * tuple(self)
        return [double_cover[i+1:j] for i, j in zip(indices[:-1], indices[1:])]

    def pinch(self, b: T, c: T, /) -> tuple[Self, Self]:
        """Pinch off the anklet into two smaller anklets.

        Bringing together and merging the two nodes `b` and `c` turns the anklet
        into a figure eight. Returns the two fundamental cycles of this figure eight,
        which share exactly one bead, as anklets.

        Parameters
        ----------
        b, c : T
            Two beads in the anklet.

        Returns
        -------
        tuple[Self, Self]
            Two anklets with only the bead `b` in common.

        Raises
        ------
        ValueError
            If either `b` or `c` is not a bead in the anklet or if `b == c`.

        Examples
        --------
        >>> Anklet.from_iterable(range(8)).pinch(2, 5)
        (A(2, 3, 4), A(2, 6, 7, 0, 1))
        >>> Anklet.from_iterable(range(8)).pinch(5, 2)
        (A(5, 3, 4), A(5, 6, 7, 0, 1))
        >>> Anklet.from_iterable(range(8)).pinch(5, 6)
        (A(5), A(5, 7, 0, 1, 2, 3, 4))
        """
        if b not in self:
            raise ValueError(f"{b!r} is not a bead in the anklet {self}")
        if c not in self:
            raise ValueError(f"{c!r} is not a bead in the anklet {self}")
        if b == c:
            raise ValueError(f"b = c = {b!r} are not distinct beads")

        i, j = sorted([self.index(b), self.index(c)])
        return (
            type(self).from_iterable(self[i:j]).replace_beads({c: b}),
            type(self).from_iterable(self[j:] + self[:i]).replace_beads({c: b})
        )


def decompose_bracelet[T: Hashable](beads: Sequence[T]) -> set[Anklet[T]]:
    """Create a set of anklets from a (cyclic) sequence of beads with no crossings.

    Consider the sequence of beads as a combinatorial bracelet, evenly spaced around the boundary
    of a topological disk. Select a bead that appears `k ≥ 2` times and draw the `k` instances
    inwards to coincide at a point in the disk's interior. This produces `k` "bulbs" joined
    at a single point: the selected bead. Each of these smaller bracelets has the selected bead
    exactly once and, by the no-crossing conditions, no other beads in common.
    Repeat this process, iteratively, until the original disk has been pinched off into a number
    of bracelets each with no repeated beads (*i.e.* anklets). It is clear that the order in which
    beads are selected to pinch off does not matter. Returns the resulting set of anklets.

    Parameters
    ----------
    beads : Sequence[T]
        A (cyclic) sequence of beads, possibly containing repeats.

    Returns
    -------
    set[Anklet[T]]
        Collection of anklets which pair-wise share at most one bead.

    Raises
    ------
    ValueError
        If the sequence of beads contains a crossing,
        *i.e.* two pairs of repeated beads which are intertwined.

    Examples
    --------
    >>> decompose_bracelet([0, 1, 2, 3, 4, 5])
    {A(0, 1, 2, 3, 4, 5)}
    >>> decompose_bracelet([0, 1, 2, 0, 3, 4, 5])
    {A(0, 3, 4, 5), A(0, 1, 2)}
    >>> decompose_bracelet([0, 1, 2, 0, 3, 0, 4, 5])
    {A(0, 3), A(0, 4, 5), A(0, 1, 2)}
    >>> decompose_bracelet([0, 1, 2, 0, 3, 4, 3, 5])
    {A(0, 1, 2), A(3, 5, 0), A(3, 4)}
    """
    beads = list(beads)
    if any(
        b1 == b3 and b2 == b4 and b1 != b2
        for b1, b2, b3, b4 in combinations(beads, 4)
    ):
        raise ValueError("the sequence of beads contains a crossing")

    anklets = set()
    queue = [beads]
    while queue:
        segment = queue.pop()
        if len(set(segment)) == len(segment):
            # No repeated beads! Add to the final set of anklets
            anklets.add(Anklet.from_iterable(segment))
            continue
        for (i, b), (j, c) in combinations(enumerate(segment), 2):
            if b == c:
                # Found a repeated bead in the segment: chop in two and add the pieces to the queue
                queue.append(segment[i:j])
                queue.append(segment[j:] + segment[:i])
                break
    return anklets


def planar_inflate[T: Hashable](anklets: Collection[Anklet[T]], b: T) -> list[set[Anklet[T]]]:
    """Join a set of anklets at a common node.

    The anklets are cut apart at the bead `b` and the resulting sequences joined end-to-end
    into a bracelet in all possible ways which avoid introducing crossings.
    Returns the decompositions of these bracelets into anklets via :meth:`decompose_bracelet`.

    Parameters
    ----------
    anklets : Collection[Anklet[T]]
        A collection of anklets, each of which contains the bead `b`.
    b : T
        A bead common to all of the anklets.

    Returns
    -------
    list[set[Anklet[T]]]
        Sets of anklets which result from the process described above.
        Within each set anklets pair-wise share at most one bead.

    Raises
    ------
    ValueError
        If one of the anklets does not contain the bead `b`.

    Examples
    --------
    >>> planar_inflate([Anklet(0, 1), Anklet(0, 2)], 0)
    [{A(2, 1)}]
    >>> planar_inflate([Anklet(0, 1, 2), Anklet(0, 1, 3)], 0)
    [{A(1, 2), A(1, 3)}, {A(1, 3, 2), A(1)}]
    >>> planar_inflate([Anklet(0, 1, 2), Anklet(0, 1, 3), Anklet(0, 4)], 0)
    [{A(1, 3), A(1, 2, 4)}, {A(1, 2, 4, 3), A(1)}, {A(1, 3, 2), A(1, 4)}, {A(1, 2), A(1, 4, 3)}]
    """
    for a in anklets:
        if b not in a:
            raise ValueError(f"{b} is not a bead in {a}")

    anklet_sets = {}
    for seq_permutation, flips in product(
        permutations([a.cut(b)[0] for a in anklets]),
        product([True, False], repeat=len(anklets))
    ):
        try:
            anklet_set = decompose_bracelet([
                bead
                for seq, flip in zip(seq_permutation, flips)
                for bead in (reversed(seq) if flip else seq)
            ])
            anklet_sets[hash(frozenset(anklet_set))] = anklet_set
        except ValueError:
            # There was a crossing
            pass
    return list(anklet_sets.values())
