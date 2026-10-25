"""Combinatorial anklets."""

from collections.abc import Collection, Container, Iterable, Iterator
from itertools import combinations
from types import NotImplementedType
from typing import Self
import networkx as nx


class Anklet[T](tuple[T, ...]):
    """An anklet is a combinatorial bracelet with all beads distinct.

    Examples
    --------
    >>> Anklet(0, 1, 2, 3) == Anklet(1, 2, 3, 0)
    True
    >>> Anklet(0, 1, 2, 3) == Anklet(0, 1, 3, 2)
    False
    >>> Anklet(0, 1, 2, 1)
    Traceback (most recent call last):
    ...
    ValueError: the beads (0, 1, 2, 1) are not distinct
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
    #   Removing beads
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def without_bead(self, bead_to_remove: T, /) -> Self:
        """Return the anklet with a bead removed.

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
        :meth:`Anklet.without_beads`

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
        """Return the anklet with beads removed.

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
        :meth:`Anklet.without_bead`

        Examples
        --------
        >>> Anklet(5, 2, 3, 0, 4, 1).without_beads((0, 2))
        A(5, 3, 4, 1)
        >>> Anklet(5, 2, 3, 0, 4, 1).without_beads(Anklet(0, 1, 6))
        A(5, 2, 3, 4)
        """
        return type(self).from_iterable(b for b in self if b not in beads_to_remove)

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

        An anklet `a` is a sub-anklet of another anklet `b` (*i.e.* `a <= b`) if the beads of `a`
        appear in the prescribed cyclic order as a subsequence of `b`. Equivalently, `a <= b` means
        that it is possible to delete beads from `b` to produce `a`.

        This "sub-anklet" relation is a partial order on anklets
        with the empty anklet of length zero as its least element.

        Parameters
        ----------
        other : object
            An anklet.

        Returns
        -------
        NotImplementedType or bool
            `NotImplemented` if `other` is not an anklet.
            Otherwise, whether this anklet is a sub-anklet of `other`.

        Examples
        --------
        >>> Anklet(0, 1, 2) <= Anklet(0, 3, 1, 4, 2, 5)
        True
        >>> Anklet(0, 1, 2, 3) <= Anklet(4, 1, 5, 3, 0, 2)
        False
        >>> Anklet() <= Anklet(0, 1, 2)
        True

        Note that comparing against a tuple reverts to `tuple.__le__`
        using the defining tuple of the anklet:

        >>> Anklet(0, 1, 2) <= (1, 2, 3, 4)
        True
        >>> (0, 2, 1) <= Anklet(0, 1, 2)
        False
        """
        if not isinstance(other, Anklet):
            return NotImplemented

        # Edge case for empty anklet to avoid IndexError below
        if not self:
            return True

        # Scan through 'other', collecting the next bead for each representative of 'self'
        # as they are passed. If a rep manages to collect all of its beads then it is a sub-anklet.
        states = {rep: 0 for rep in self.representatives()}
        for bead in other:
            for rep, index in states.items():
                if bead == rep[index]:
                    states[rep] += 1
                    if states[rep] == len(self):
                        return True
        return False

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

    def standardized(self) -> Self:
        """Return an equivalent anklet with minimal defining tuple.

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
        >>> Anklet(0j, 1j).standardized()
        Traceback (most recent call last):
        ...
        TypeError: '<' not supported between instances of 'complex' and 'complex'
        """
        return type(self).from_iterable(min(self.representatives()))

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
        # one for the parent anklet and one each for the subanklets corresponding to 'x' and 'y'
        subanklet_x = Anklet.from_iterable(bead for bead in self if bead in x)
        subanklet_y = Anklet.from_iterable(bead for bead in self if bead in y)
        g = nx.disjoint_union_all(a.to_wheel_graph() for a in [self, subanklet_x, subanklet_y])

        # Join nodes which share a bead label
        label_groups = {}
        for n, label in nx.get_node_attributes(g, 'anklet').items():
            if label not in label_groups:
                label_groups[label] = set()
            label_groups[label].add(n)
        for node_group in label_groups.values():
            for u, v in combinations(node_group, 2):
                g.add_edge(u, v)

        return nx.is_planar(g)
