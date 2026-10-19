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
    ValueError: beads are not distinct
    """

    def __new__(cls, *beads: T) -> Self:
        if len(set(beads)) != len(beads):
            raise ValueError("beads are not distinct")
        return super().__new__(cls, beads)

    @classmethod
    def from_iterable(cls, beads: Iterable[T] = (), /) -> Self:
        """Construct an anklet from an iterable of beads.

        Unlike `Anklet(x)`, this method treats `x` as a source of beads
        rather than as the lone bead of the anklet.

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

    def representatives(self) -> Iterator[tuple[T, ...]]:
        """Generate all representative tuples of the anklet.

        For an anklet of length `n ≥ 3`, yields the `2n` images of its defining tuple under
        the action of `Dihₙ`. Anklets of length `n ≤ 1` and `n = 2` yield only one and two
        representatives, respectively.

        Yields
        ------
        tuple[T, ...]
            A representative tuple, equivalent to the defining tuple
            up to cyclic permutation and reversal.

        Examples
        --------
        >>> list(Anklet().representatives())
        [()]
        >>> list(Anklet(0).representatives())
        [(0,)]
        >>> sorted(Anklet(0, 1).representatives())
        [(0, 1), (1, 0)]
        >>> sorted(Anklet(0, 1, 2).representatives())
        [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
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
        """Return whether the anklet is a sub-anklet of `other`.

        This "sub-anklet" partial order has the empty anklet of length zero as its least element.

        Parameters
        ----------
        other : object
            Anklet against which to compare this anklet.

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

        See :meth:`__le__` for the definition of the underlying partial order on anklets.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return len(self) < len(other) and self <= other

    def __ge__(self, other: object) -> NotImplementedType:
        """Return whether `other <= self`.

        See :meth:`__le__` for the definition of the underlying partial order on anklets.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return other <= self

    def __gt__(self, other: object) -> NotImplementedType:
        """Return whether `other <= self` and `self != other`.

        See :meth:`__le__` for the definition of the underlying partial order on anklets.
        """
        if not isinstance(other, Anklet):
            return NotImplemented
        return len(other) < len(self) and other <= self

    def without_bead(self, bead: T, /) -> Self:
        """Return the anklet with a bead removed.

        The relative order of all retained beads is preserved.

        Parameters
        ----------
        bead : T
            Bead to remove.

        Returns
        -------
        Self
            The anklet with `bead` removed, if present.

        See Also
        --------
        :meth:`without_beads`

        Examples
        --------
        >>> a = Anklet(5, 2, 3, 0, 4, 1)
        >>> a.without_bead(3)
        A(5, 2, 0, 4, 1)
        >>> a.without_bead(6)
        A(5, 2, 3, 0, 4, 1)
        """
        return type(self).from_iterable(b for b in self if b is not bead)

    def without_beads(self, beads: Container[T], /) -> Self:
        """Return the anklet with beads removed.

        Parameters
        ----------
        beads : Container[T]
            Beads to remove.

        Returns
        -------
        Self
            Anklet with beads from `beads` removed, if present.

        See Also
        --------
        :meth:`without_bead`

        Examples
        --------
        >>> Anklet(5, 2, 3, 0, 4, 1).without_beads((0, 2))
        A(5, 3, 4, 1)
        >>> Anklet(5, 2, 3, 0, 4, 1).without_beads(Anklet(0, 1, 6))
        A(5, 2, 3, 4)
        """
        return type(self).from_iterable(b for b in self if b not in beads)

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

        An anklet of length `n` is represented by the wheel graph `Wₙ` on the nodes `0, 1, ..., n`;
        the central node is `0` and the nodes `1, 2, ..., n` form the outer `n`-cycle.
        Note that for `n = 1` and `n = 2` the graph degenerates and has fewer than `2n` edges.

        The nodes in the `n`-cycle have an 'anklet' attribute with values the beads of the anklet.

        Returns
        -------
        networkx.Graph
            A wheel graph labeled by the anklet.

        Examples
        --------
        >>> g = Anklet('a', 'b', 'c', 'd').to_wheel_graph()
        >>> print(g)
        Graph with 5 nodes and 8 edges
        >>> nx.get_node_attributes(g, 'anklet')
        {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
        >>> sorted(g.edges)
        [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
        """
        g = nx.wheel_graph(len(self) + 1)
        nx.set_node_attributes(g, dict(enumerate(self, start=1)), 'anklet')
        return g

    def noncrossing(self, x: Collection[T], y: Collection[T]) -> bool:
        """Return whether the collections of beads `x` and `y` in the anklet are non-crossing.

        Returns `False` if the anklet does not contain all elements from both `x` and `y`.

        Otherwise, consider arranging the beads of the anklet on the boundary of a disk
        in the prescribed cyclic order and joining the elements of `x` and `y` into sub-anklets
        via a series of chords. Return `True` if the interiors of the chord cycles corresponding
        to `x` and y` are disjoint and `False` if they intersect.

        Note that the sets `x` and `y` need not be disjoint;
        their corresponding sub-anklets may meet at up to two points without forcing a crossing.

        Examples
        --------
        >>> a = Anklet.from_iterable(range(6))

        A triangle and digon which are disjoint:

        >>> a.noncrossing({0, 1, 2}, {3, 4})
        True

        Two triangles which meet at a vertex:

        >>> a.noncrossing({0, 1, 2}, {2, 3, 4})
        True

        Two triangles which meet at two vertices:

        >>> a.noncrossing({0, 2, 5}, {2, 3, 5})
        True

        Two triangles which cross:

        >>> a.noncrossing({0, 1, 4}, {2, 3, 5})
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
