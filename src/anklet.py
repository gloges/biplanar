"""Combinatorial anklets."""

from collections.abc import Container, Hashable, Iterable, Iterator
from types import NotImplementedType
from typing import Self


class Anklet[T: Hashable](tuple[T, ...]):
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
