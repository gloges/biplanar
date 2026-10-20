"""Anklet graphs."""

from collections.abc import Collection, Hashable, Iterable, Iterator, Mapping
from itertools import combinations
from types import NotImplementedType
from typing import Any, Self, Literal
import networkx as nx
from anklet import Anklet


class AnkletGraph[T: Hashable]:
    """An **anklet graph** is a multi-hypergraph with additional combinatorial structure.

    A hyperedge in an anklet graph is represented by a finite sequence of unique incident nodes
    considered up to cyclic rotation and reversal: an *anklet*. That is, each hyperedge specifies
    a cylic ordering of its incidences with no chosen orientation or distinguished starting point.

    Forgetting the anklet structure of the hyperedges yields an ordinary multi-hypergraph:
    each hyperedge is simply incident to the set of nodes appearing in its sequence.

    An embedding of an anklet graph into a surface must preserve the anklet structure
    of its hyperedges. This means that a hyperedge must be embedded as a topological disk
    with the incident nodes appearing on the boundary in the prescribed cyclic order.
    """

    _name: str
    _attr: dict[str, Any]
    _node: dict[T, dict[str, Any]]
    _edge: dict[Anklet[T], int]
    _reduced: None | Literal[True]

    def __init__(self, nodes: Iterable[T] = (), *, name: str = "", **attr: Any) -> None:
        self._name = name
        self._attr = attr
        self._node = {}
        self._edge = {}

        self.add_nodes_from(nodes)
        self._reduced = True

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

    def __str__(self) -> str:
        """Return a short summary of the graph.

        Examples
        --------
        >>> g = AnkletGraph(range(5), name='myGraph', color='b', type='foo')
        >>> g.add_hyperedges_from({Anklet(0, 1, 2): 1, Anklet(2, 3, 4): 2})
        >>> print(g)
        AnkletGraph named myGraph with attribute(s) (color, type), 5 nodes and 3 hyperedges
        """
        return "".join([
            type(self).__name__,
            f" named {self._name}" if self._name else "",
            " with attribute(s) (" + ", ".join(self._attr) + ")," if self._attr else " with",
            f" {self.number_of_nodes()} nodes"
            f" and {self.number_of_hyperedges()} hyperedges",
        ])

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

    def copy(self) -> Self:
        """Return a copy of the anklet graph.

        Graph attributes, nodes, node attributes and hyperedges are copied.
        If the graph has a name then '-copy' is appended: otherwise the copy remains unnamed.

        Returns
        -------
        Self
            A copy of the anklet graph.
        """
        g = type(self)(name=self.name + '-copy' if self.name else '', **self._attr.copy())
        g.add_nodes_from(self._node.copy())
        g.add_hyperedges_from(self._edge.copy())
        g._reduced = self._reduced  # pylint: disable=W0212:protected-access
        return g

    def get_data_strings(self) -> tuple[str, str]:
        """Return two strings summarizing the node and hyperedge data of the anklet graph.

        Returns
        -------
        node_data, hyperedge_data : str
            The first returned string is a comma-separated list of the nodes.
            The second returned string contains the hyperedges with their multiplicities,
            each formated as `"k × A(...)"` (or simply `"A(...)"` if `k = 1`), joined by `" + "`.

        Examples
        --------
        >>> g = AnkletGraph(range(5))
        >>> g.add_hyperedges_from({Anklet(0): 3, Anklet(0, 1): 2, Anklet(1, 2, 3): 1})
        >>> g.get_data_strings()
        ('0, 1, 2, 3, 4', '3 × A(0) + 2 × A(0, 1) + A(1, 2, 3)')
        """
        return (
            ", ".join(str(n) for n in self._node),
            " + ".join(f"{k} × {hype}" if k > 1 else str(hype) for hype, k in self._edge.items())
        )

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Graph attributes
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def get_attribute(self, attr_name: str) -> Any:
        """Return a graph attribute.

        Parameters
        ----------
        attr_name : str
            Attribute name.

        Returns
        -------
        Any
            Attribute value.

        Raises
        ------
        KeyError
            If the graph has no attribute `attr_name`.

        See Also
        --------
        :meth:`set_attributes`,
        :meth:`remove_attribute`,
        :meth:`clear_attributes`

        Examples
        --------
        >>> g = AnkletGraph(range(5), name='myGraph', color='b')
        >>> g.get_attribute('color')
        'b'

        The graph's name is *not* an attribute:

        >>> g.get_attribute('name')
        Traceback (most recent call last):
        ...
        KeyError: 'name'
        """
        return self._attr[attr_name]

    def set_attributes(self, **attr: Any) -> None:
        """Set or overwrite graph attributes.

        Parameters
        ----------
        attr : keyword arguments
            Set or change attributes using key=value.

        Raises
        ------
        KeyError
            If the attribute keys include "name".

        See Also
        --------
        :meth:`get_attribute`,
        :meth:`remove_attribute`,
        :meth:`clear_attributes`

        Examples
        --------
        >>> g = AnkletGraph(range(5), name='myGraph', color='r', type='foo')
        >>> g.set_attributes(type='bar', acyclic=False)
        >>> g.get_attribute('type')
        'bar'
        >>> g.get_attribute('acyclic')
        False
        >>> g.set_attributes(name='yourGraph')
        Traceback (most recent call last):
        ...
        KeyError: "'name' cannot be an attribute."
        """
        if 'name' in attr:
            raise KeyError("'name' cannot be an attribute.")
        self._attr.update(attr)

    def remove_attribute(self, attr_name: str) -> None:
        """Remove a graph attribute.

        Returns quietly if the attribute does not exist.

        Parameters
        ----------
        attr_name : str
            Attribute name.

        See Also
        --------
        :meth:`get_attribute`,
        :meth:`set_attributes`,
        :meth:`clear_attributes`
        """
        if attr_name in self._attr:
            self._attr.pop(attr_name)

    def clear_attributes(self) -> None:
        """Remove all graph attributes.

        The graph's name, nodes and hyperedges are left unchanged.

        See Also
        --------
        :meth:`get_attribute`,
        :meth:`set_attributes`,
        :meth:`remove_attribute`,
        :meth:`clear_hyperedges`,
        :meth:`clear`
        """
        self._attr.clear()

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

    def add_node(self, n: T, **attr: dict[str, Any]) -> None:
        """Add a node and update its attributes.

        Parameters
        ----------
        n : T
            The node to add to the graph.
        attr : keyword arguments, optional
            Set or change node attributes using key=value.

        See Also
        -------
        :meth:`add_nodes_from`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_node(0, color='r')
        >>> g.nodes
        {0}
        >>> g.get_node_attributes('color')
        {0: 'r'}
        >>> g.add_node(0, color='g', weight=5)
        >>> g.nodes
        {0}
        >>> g.get_node_attributes('color')
        {0: 'g'}
        >>> g.get_node_attributes('weight')
        {0: 5}
        """
        if n not in self._node:
            self._node[n] = {}
        self._node[n].update(attr)

    def add_nodes_from(self, nodes: Iterable[T], **attr: dict[str, Any]) -> None:
        """Add multiple nodes.

        Parameters
        ----------
        nodes : Iterable[T]
            A container (list, dict, set, etc.) of nodes to add.
            If `nodes` is a `Mapping` then the values are used to update node attributes.
        attr : keyword arguments, optional
            Update attributes for all nodes in nodes. Node attributes specified in nodes
            take precedence over attributes specified via keyword arguments.

        See Also
        --------
        :meth:`add_node`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_nodes_from(range(2))
        >>> g.nodes
        {0, 1}
        >>> g.add_nodes_from({1: {'weight': 2}, 2: {'weight': 5, 'color': 'r'}, 3: {}}, weight=0)
        >>> g.nodes
        {0, 1, 2, 3}
        >>> g.get_node_attributes('color')
        {2: 'r'}
        >>> g.get_node_attributes('weight')
        {1: 2, 2: 5, 3: 0}
        """
        for n in nodes:
            if n not in self:
                self._node[n] = {}
            self._node[n].update(attr)
            if isinstance(nodes, Mapping):
                self._node[n].update(nodes[n])

    def remove_node(self, n: T) -> None:
        """Remove a node and all incident hyperedges.

        Parameters
        ----------
        n : T
            A node in the graph.

        Raises
        ------
        ValueError
            If `n` is not in the graph.

        See Also
        --------
        :meth:`remove_nodes_from`,
        :meth:`erase_node`,
        :meth:`erase_nodes_from`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2): 2, Anklet(2, 3, 4): 3})
        >>> g.nodes
        {0, 1, 2, 3, 4}
        >>> g.remove_node(1)
        >>> g.nodes
        {0, 2, 3, 4}
        >>> g.hyperedges
        ((A(2, 3, 4), 3),)
        """
        if n not in self.nodes:
            raise ValueError(f"the node {n} is not in the graph")
        self._node.pop(n)
        self.remove_hyperedges_from({hype: k for hype, k in self._edge.items() if n in hype})

    def remove_nodes_from(self, nodes: Iterable[T]) -> None:
        """Remove multiple nodes.

        Parameters
        ----------
        nodes : Iterable[T]
            A container (list, dict, set, etc.) of nodes.
            If a node from `nodes` is not in the graph it is silently ignored.

        See Also
        --------
        :meth:`remove_node`,
        :meth:`erase_node`,
        :meth:`erase_nodes_from`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2): 2, Anklet(2, 3, 4): 3})
        >>> g.nodes
        {0, 1, 2, 3, 4}
        >>> g.remove_nodes_from((2, 4, 'a'))
        >>> g.nodes
        {0, 1, 3}
        >>> g.hyperedges
        ((A(0, 1), 1),)
        """
        for n in nodes:
            try:
                self.remove_node(n)
            except ValueError:
                pass

    def erase_node(self, n: T) -> None:
        """Remove a node and erase it from all incident hyperedges.

        Parameters
        ----------
        n : T
            A node in the graph.

        Raises
        ------
        ValueError
            If `n` is not in the graph.

        See Also
        --------
        :meth:`remove_node`,
        :meth:`remove_nodes_from`,
        :meth:`erase_nodes_from`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(1): 3, Anklet(0, 1, 4): 2, Anklet(1, 2, 3, 4): 1})
        >>> g.nodes
        {0, 1, 2, 3, 4}
        >>> g.erase_node(1)
        >>> g.nodes
        {0, 2, 3, 4}
        >>> g.hyperedges
        ((A(0, 4), 2), (A(2, 3, 4), 1))
        """
        if n not in self.nodes:
            raise ValueError(f"the node {n} is not in the graph")
        self._node.pop(n)
        self._edge = {hype.without_bead(n): k for hype, k in self._edge.items()}
        if Anklet() in self._edge:
            self._edge.pop(Anklet())

        # Erasing a node from a reduced graph may make it reducible
        self._reduced = None

    def erase_nodes_from(self, nodes: Iterable[T]) -> None:
        """Erase multiple nodes.

        Parameters
        ----------
        nodes : Iterable[T]
            A container (list, dict, set, etc.) of nodes.
            If a node from `nodes` is not in the graph it is silently ignored.

        See Also
        --------
        :meth:`remove_node`,
        :meth:`remove_nodes_from`,
        :meth:`erase_node`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(1): 3, Anklet(0, 1, 4): 2, Anklet(1, 2, 3, 4): 1})
        >>> g.nodes
        {0, 1, 2, 3, 4}
        >>> g.erase_nodes_from((1, 3, 5))
        >>> g.nodes
        {0, 2, 4}
        >>> g.hyperedges
        ((A(0, 4), 2), (A(2, 4), 1))
        """
        for n in nodes:
            try:
                self.erase_node(n)
            except ValueError:
                pass

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Node attributes
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def get_node_attributes(self, attr_name: str, default: Any = None) -> dict[T, Any]:
        """Return node attributes.

        Parameters
        ----------
        attr_name : str
            Attribute name.
        default : Any, optional (default=None)
            Default value of the node attribute if there is no value set for a node
            in the anklet graph. If `None` then nodes without this attribute
            are not included in the returned dict.

        Returns
        -------
        dict[T, Any]
            Attributes keyed by node.

        See Also
        --------
        :meth:`set_node_attributes`,
        :meth:`remove_node_attributes`

        Examples
        --------
        >>> g = AnkletGraph(range(5))
        >>> g.set_node_attributes('color', {0: 1, 1: 2.5, 3: 'c'})
        >>> g.get_node_attributes('color')
        {0: 1, 1: 2.5, 3: 'c'}
        >>> g.get_node_attributes('color', 'r')
        {0: 1, 1: 2.5, 2: 'r', 3: 'c', 4: 'r'}
        """
        if default is not None:
            return {n: d.get(attr_name, default) for n, d in self._node.items()}
        return {n: d[attr_name] for n, d in self._node.items() if attr_name in d}

    def set_node_attributes(self, attr_name: str, values: Mapping[T, Any]) -> None:
        """Set or update node attributes.

        Parameters
        ----------
        attr_name : str
            Attribute name.
        values : Mapping[T, Any]
            Attribute values keyed by nodes of the anklet graph.
            Keys which are not nodes in the graph are silently ignored.

        See Also
        --------
        :meth:`get_node_attributes`,
        :meth:`remove_node_attributes`

        Examples
        --------
        >>> g = AnkletGraph(range(5))
        >>> g.set_node_attributes('weight', {0: 1, 1: 2.5, 'a': 'b', 3: 'c'})
        >>> g.get_node_attributes('weight')
        {0: 1, 1: 2.5, 3: 'c'}
        """
        for n, val in values.items():
            try:
                self._node[n][attr_name] = val
            except KeyError:
                pass

    def remove_node_attributes(self, attr_name: str, nodes: Collection[T] | None = None) -> None:
        """Remove node attributes.

        Parameters
        ----------
        attr_name : str
            Attribute name.
        nodes : Collection[T] or None, optional (default=None)
            Nodes from which to remove the attribute.
            If `None`, the attribute is removed from *all* nodes.

        See Also
        --------
        :meth:`get_node_attributes`,
        :meth:`set_node_attributes`

        Examples
        --------
        >>> g = AnkletGraph(range(5))
        >>> g.set_node_attributes('color', dict(enumerate('abcde')))
        >>> g.get_node_attributes('color')
        {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}
        >>> g.remove_node_attributes('color', [0, 3])
        >>> g.get_node_attributes('color')
        {1: 'b', 2: 'c', 4: 'e'}
        >>> g.remove_node_attributes('color')
        >>> g.get_node_attributes('color')
        {}
        """
        for n in self:
            if nodes is None or n in nodes:
                if attr_name in self._node[n]:
                    self._node[n].pop(attr_name)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Hyperedges
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    @property
    def hyperedges(self) -> tuple[tuple[Anklet[T], int], ...]:
        """The hyperedges and their multiplicities."""
        return tuple((hype, k) for hype, k in self._edge.items())

    def _all_hyperedges(self) -> list[Anklet[T]]:
        """Return a list of the hyperedges with multiplicity."""
        return [hype for hypes in [k * [hype] for hype, k in self._edge.items()] for hype in hypes]

    def number_of_hyperedges(self) -> int:
        """Return the number of hyperedges (counted with multiplicity).

        Returns
        -------
        int
            The total number of hyperedges in the graph.

        See Also
        --------
        :meth:`number_of_unique_hyperedges`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2): 2, Anklet(2, 3, 4): 3})
        >>> g.number_of_hyperedges()
        6
        """
        return sum(self._edge.values())

    def number_of_unique_hyperedges(self) -> int:
        """Return the number of unique hyperedges (i.e. counted without multiplicity).

        Returns
        -------
        int
            The number of unique hyperedges in the graph.

        See Also
        --------
        :meth:`number_of_hyperedges`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2): 2, Anklet(2, 3, 4): 3})
        >>> g.number_of_unique_hyperedges()
        3
        """
        return len(self._edge)

    def add_hyperedge(self, hype: Anklet[T], k: int = 1) -> None:
        """Add a hyperedge.

        If the hyperedge is already present then its multiplicity is increased by `k`.
        Otherwise, the hyperedge is added to the graph and its multiplicity set to `k`.
        The hyperedge's incident nodes will be automatically added to the graph
        if they are not already present.

        Parameters
        ----------
        hype : Anklet[T]
            The hyperedge to add to the graph.
        k : int, optional (default=1)
            The number of copies of `hype` to add.

        Raises
        ------
        ValueError
            If `k` is not a positive integer.

        See Also
        --------
        :meth:`add_hyperedges_from`

        Examples
        --------
        >>> hype = Anklet(0, 1, 2)
        >>> g = AnkletGraph()
        >>> g.add_hyperedge(hype, 2)
        >>> g.nodes
        {0, 1, 2}
        >>> g.hyperedges
        ((A(0, 1, 2), 2),)
        >>> g.add_hyperedge(hype, 3)
        >>> g.hyperedges
        ((A(0, 1, 2), 5),)
        """
        if not isinstance(k, int) or k <= 0:
            raise ValueError(f"k={k} is not a positive integer")

        self.add_nodes_from(hype)
        if hype not in self._edge:
            self._edge[hype] = 0
        self._edge[hype] += k

        # Adding a hyperedge can make a reduced graph reducible
        self._reduced = None

    def add_hyperedges_from(self, hypes: Iterable[Anklet[T]]) -> None:
        """Add multiple hyperedges.

        Parameters
        ----------
        hypes: Iterable[Anklet[T]]
            A container (list, dict, set, etc.) of hyperedges.
            If `hypes` is a Mapping then the values are interpreted as the number of copies
            of each hyperedge to add; otherwise, one instance of each hyperedge is added.

        See Also
        --------
        :meth:`add_hyperedge`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from([Anklet(0, 1), Anklet(1, 2, 3, 4)])
        >>> g.nodes
        {0, 1, 2, 3, 4}
        >>> g.hyperedges
        ((A(0, 1), 1), (A(1, 2, 3, 4), 1))
        >>> g.add_hyperedges_from({Anklet(1, 2, 3, 4): 2, Anklet(0, 2): 2})
        >>> g.hyperedges
        ((A(0, 1), 1), (A(1, 2, 3, 4), 3), (A(0, 2), 2))
        """
        if isinstance(hypes, Mapping):
            for hype, k in hypes.items():
                self.add_hyperedge(hype, k)
        else:
            for hype in hypes:
                self.add_hyperedge(hype)

    def remove_hyperedge(self, hype: Anklet[T], k: int = 1) -> None:
        """Remove a hyperedge.

        The hyperedge `hype` must be present in the graph. The multiplicity of `hype` is reduced
        by `k` and if it drops to zero the hyperedge is removed.

        Parameters
        ----------
        hype : Anklet[T]
            The hyperedge to remove from the graph.
        k : int, optional (default=1)
            The number of copies of `hype` to remove.

        Raises
        ------
        ValueError
            If `hype` is not a hyperedge in the graph, if `k` is not a positive integer,
            or if `k` exceeds the multiplicity of `hype`.

        See Also
        --------
        :meth:`remove_hyperedges_from`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 2, Anklet(1, 2, 3, 4): 3, Anklet(0, 2): 4})
        >>> g.hyperedges
        ((A(0, 1), 2), (A(1, 2, 3, 4), 3), (A(0, 2), 4))
        >>> g.remove_hyperedge(Anklet(1, 0))
        >>> g.hyperedges
        ((A(0, 1), 1), (A(1, 2, 3, 4), 3), (A(0, 2), 4))
        >>> g.remove_hyperedge(Anklet(4, 3, 2, 1), 3)
        >>> g.hyperedges
        ((A(0, 1), 1), (A(0, 2), 4))
        >>> g.remove_hyperedge(Anklet(0, 2), 5)
        Traceback (most recent call last):
        ...
        ValueError: 5 > 4 is larger than the multiplicity of hyperedge A(0, 2)
        """
        if hype not in self._edge:
            raise ValueError(f"{hype} is not a hyperedge in the graph")
        if not isinstance(k, int) or k <= 0:
            raise ValueError(f"k={k} is not a positive integer")
        if k > self._edge[hype]:
            raise ValueError(
                f"{k} > {self._edge[hype]} is larger than the multiplicity of hyperedge {hype}"
            )

        self._edge[hype] -= k
        if self._edge[hype] == 0:
            self._edge.pop(hype)

    def remove_hyperedges_from(self, hypes: Iterable[Anklet[T]]) -> None:
        """Remove multiple hyperedges.

        Parameters
        ----------
        hypes : Iterable[Anklet[T]]
            A container (list, dict, set, etc.) of hyperedges.
            If `hypes` is a Mapping then the values are interpreted as the number of copies
            of each hyperedge to remove; otherwise, one instance of each hyperedge is removed.

        See Also
        --------
        :meth:`remove_hyperedge`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2, 3, 4): 2, Anklet(0, 2): 3})
        >>> g.hyperedges
        ((A(0, 1), 1), (A(1, 2, 3, 4), 2), (A(0, 2), 3))
        >>> g.remove_hyperedges_from([Anklet(0, 2), Anklet(0, 1)])
        >>> g.hyperedges
        ((A(1, 2, 3, 4), 2), (A(0, 2), 2))
        >>> g.remove_hyperedges_from({Anklet(2, 0): 1, Anklet(3, 2, 1, 4): 2})
        >>> g.hyperedges
        ((A(0, 2), 1),)
        """
        if isinstance(hypes, Mapping):
            for hype, k in hypes.items():
                self.remove_hyperedge(hype, k)
        else:
            for hype in hypes:
                self.remove_hyperedge(hype)

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Clear nodes / hyperedges
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def clear_hyperedges(self) -> None:
        """Remove all hyperedges.

        The graph's name, attributes and nodes are left unchanged.

        See Also
        --------
        :meth:`clear_attributes`,
        :meth:`clear`
        """
        self._edge.clear()
        self._reduced = True

    def clear(self) -> None:
        """Remove all nodes and hyperedges.

        The graph's name and attributes are left unchanged.

        See Also
        --------
        :meth:`clear_attributes`,
        :meth:`clear_hyperedges`
        """
        self.clear_hyperedges()
        self._node.clear()

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Incidence / adjacency
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def incidence(self) -> dict[T, set[Anklet[T]]]:
        """Return the incidence data.

        Returns
        -------
        dict[T, set[Anklet[T]]]
            Dictionary keyed by nodes.
            Values are the sets of hyperedges in the graph containing that node.

        See Also
        --------
        :meth:`adjacency`,
        :meth:`anklet_adjacency`,
        :meth:`to_incidence_graph`

        Examples
        --------
        >>> g = AnkletGraph(range(4))
        >>> g.add_hyperedges_from({Anklet(0, 1): 2, Anklet(1): 3, Anklet(0, 2): 4})
        >>> g.incidence()
        {0: {A(0, 1), A(0, 2)}, 1: {A(0, 1), A(1)}, 2: {A(0, 2)}, 3: set()}
        """
        inc = {n: set() for n in self}
        for hype in self._edge:
            for n in hype:
                inc[n].add(hype)
        return inc

    def adjacency(self) -> dict[T, set[T]]:
        """Return the adjacency data.

        Two nodes are adjacent if they appear together in one or more hyperedge.

        Note that a node is never adjacent to itself.

        Returns
        -------
        dict[T, set[T]]
            Dictionary keyed by nodes. Values are the sets of adjacent nodes.

        See Also
        --------
        :meth:`incidence`,
        :meth:`anklet_adjacency`,
        :meth:`to_adjacency_graph`

        Examples
        --------
        >>> g = AnkletGraph(range(5))
        >>> g.add_hyperedges_from({Anklet(0, 1): 2, Anklet(1): 3, Anklet(0, 2, 3): 4})
        >>> g.adjacency()
        {0: {1, 2, 3}, 1: {0}, 2: {0, 3}, 3: {0, 2}, 4: set()}
        """
        adj = {n: set() for n in self}
        for hype in self._edge:
            for u, v in combinations(hype, 2):
                adj[u].add(v)
                adj[v].add(u)
        return adj

    def anklet_adjacency(self) -> dict[T, set[T]]:
        """Return the anklet adjacency data.

        Nodes are anklet-adjacent if they appear sequentially in one or more hyperedge.

        Note that a node `n` is anklet-adjacent to itself *if and only if* the hyperedge `A(n)`
        is present in the graph.

        Returns
        -------
        dict[T, set[T]]
            Dictionary keyed by nodes. Values are the sets of anklet-adjacent nodes.

        See Also
        --------
        :meth:`incidence`,
        :meth:`adjacency`

        Examples
        --------
        >>> g = AnkletGraph(range(6))
        >>> g.add_hyperedges_from({Anklet(0, 1, 2, 3, 4): 2, Anklet(1): 3})
        >>> g.anklet_adjacency()
        {0: {1, 4}, 1: {0, 1, 2}, 2: {1, 3}, 3: {2, 4}, 4: {0, 3}, 5: set()}
        """
        adj = {n: set() for n in self}
        for hype in self._edge:
            for i, n in enumerate(hype):
                adj[n].add(hype[i-1])
                adj[hype[i-1]].add(n)
        return adj

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Associated graphs
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def to_incidence_graph(self) -> nx.Graph:
        """Return the simple graph reflecting node-hyperedge incidences in the anklet graph.

        The returned graph has the *nodes* and *hyperedges* of the anklet graph for nodes
        and edges between "node" nodes and "hyperedge" nodes when they are incident:
        this is a simple, bipartite graph.

        Since hyperedges of the anklet graph can have multiplicities larger than one,
        the "hyperedge" nodes in the returned simple graph are pairs `(anklet, index)`
        where `index` is a unique integer.

        Returns
        -------
        networkx.Graph
            A simple, bipartite graph on the nodes and hyperedges of the anklet graph.

        See Also
        --------
        :meth:`incidence`,
        :meth:`to_adjacency_graph`,
        :meth:`to_wheel_graph`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2, 3): 2})
        >>> inc_graph = g.to_incidence_graph()
        >>> list(inc_graph.nodes)
        [0, 1, 2, 3, (A(0, 1), 0), (A(1, 2, 3), 0), (A(1, 2, 3), 1)]
        >>> inc_graph.number_of_edges()
        8
        >>> nx.is_bipartite(inc_graph)
        True
        """
        g = nx.Graph()
        g.add_nodes_from(self._node)
        for hype, k in self._edge.items():
            for i in range(k):
                g.add_edges_from((n, (hype, i)) for n in hype)
        return g

    def to_adjacency_graph(self) -> nx.Graph:
        """The simple graph reflecting node adjacencies in the anklet graph.

        The returned graph has the same nodes as the anklet graph but two nodes are joined
        by an edge if they appear together in one or more hyperedge of the anklet graph.

        Returns
        -------
        networkx.Graph
            A simple graph on the nodes of the anklet graph.

        See Also
        --------
        :meth:`adjacency`,
        :meth:`to_incidence_graph`,
        :meth:`to_wheel_graph`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from({Anklet(0, 1): 1, Anklet(1, 2, 3): 2})
        >>> adj_graph = g.to_adjacency_graph()
        >>> sorted(adj_graph.nodes)
        [0, 1, 2, 3]
        >>> sorted(adj_graph.edges)
        [(0, 1), (1, 2), (1, 3), (2, 3)]
        """
        g = nx.Graph()
        g.add_nodes_from(self._node)
        for n, nbrs in self.adjacency().items():
            for nbr in nbrs:
                g.add_edge(n, nbr)
        return g

    def to_wheel_graph(self) -> nx.Graph:
        """The simple graph formed by representing each hyperedge by a wheel graph.

        Each hyperedge is turned into a wheel graph using :meth:`Anklet.to_wheel_graph`.
        The nodes in the outer cycles of the wheels are then joined via edges to the node
        of the anklet graph according to the anklet structure of the hyperedge.

        Returns
        -------
        networkx.Graph
            A simple graph whose nodes are both the nodes of the anklet graph
            as well as `n + 1` integer nodes for each hyperedge of size `n`.

        See Also
        --------
        :meth:`to_incidence_graph`,
        :meth:`to_adjacency_graph`,
        :meth:`Anklet.to_wheel_graph`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedge(Anklet('a', 'b', 'c'))
        >>> wh_graph = g.to_wheel_graph()
        >>> sorted(wh_graph.nodes, key=lambda x: (isinstance(x, int), x))
        ['a', 'b', 'c', 0, 1, 2, 3]
        >>> sorted(wh_graph.edges, key=lambda x: (isinstance(x[1], int), x))
        [(1, 'a'), (2, 'b'), (3, 'c'), (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        """

        # Turn each hyperedge into a (labeled) wheel graph and take their disjoint union
        if self._edge:
            g = nx.disjoint_union_all([hype.to_wheel_graph() for hype in self._all_hyperedges()])
        else:
            g = nx.Graph()

        # To avoid collisions, relabel the nodes of 'g' (in place)
        # by shifting above the largest int in self._node (if any)
        shift = 0
        for n in self._node:
            if isinstance(n, int) and shift <= n:
                shift = n + 1
        nx.relabel_nodes(g, {i: i + shift for i in g}, copy=False)

        # Add the anklet graph nodes to 'g' and join the labeled wheel graph nodes
        # to the node recorded by their 'anklet' attribute
        g.add_nodes_from(self._node)
        g.add_edges_from(nx.get_node_attributes(g, 'anklet').items())

        return g

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Planarity
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def is_planar(self) -> bool:
        """Return whether the anklet graph is planar.

        The anklet structure of the hyperedges plays a key role: each hyperedge must
        be embedded into the plane as a topological disk with incident nodes organized
        on the boundary in the prescribed order.

        Examples
        --------
        >>> g = AnkletGraph(range(3))
        >>> g.is_planar()
        True
        >>> g.add_hyperedge(Anklet(0, 1, 2))
        >>> g.is_planar()
        True
        >>> g.add_hyperedge(Anklet(0, 1, 2))
        >>> g.is_planar()
        True
        >>> g.add_hyperedge(Anklet(0, 1, 2))
        >>> g.is_planar()
        False
        """
        return nx.is_planar(self.to_wheel_graph())

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Connectivity
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def connected_components(self) -> Iterator[set[T]]:
        """Generate connected components.

        Yields
        ------
        set[T]
            Set of nodes of a connected component.

        Examples
        --------
        >>> g = AnkletGraph(range(7))
        >>> g.add_hyperedges_from([Anklet(0, 1, 2), Anklet(2, 3)])
        >>> list(g.connected_components())
        [{0, 1, 2, 3}, {4}, {5}, {6}]
        >>> g.add_hyperedges_from([Anklet(4), Anklet(5, 6)])
        >>> list(g.connected_components())
        [{0, 1, 2, 3}, {4}, {5, 6}]
        >>> g.add_hyperedge(Anklet(0, 4, 6))
        >>> list(g.connected_components())
        [{0, 1, 2, 3, 4, 5, 6}]
        """
        return nx.connected_components(self.to_adjacency_graph())

    def is_connected(self) -> bool:
        """Return whether the anklet graph is connected.

        Returns
        -------
        bool
            `True` if the anklet graph is connected, `False` otherwise.

        See Also
        --------
        :meth:`connected_components`,
        :meth:`is_biconnected`

        Examples
        --------
        >>> g = AnkletGraph(range(4))
        >>> g.add_hyperedge(Anklet(0, 1, 2))
        >>> g.is_connected()
        False
        >>> g.add_hyperedge(Anklet(2, 3))
        >>> g.is_connected()
        True
        """
        return nx.is_connected(self.to_adjacency_graph())

    def is_biconnected(self) -> bool:
        """Return whether the anklet graph is biconnected.

        An anklet graph is biconnected *if and only if* it cannot be disconnected by *erasing*
        one node. Note that in erasing a node its incident hyperedges are *not* removed
        if they are incident to other other nodes.

        Returns
        -------
        bool
            `True` if the anklet graph is biconnected, `False` otherwise.

        See Also
        --------
        :meth:`connected_components`,
        :meth:`is_connected`

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedge(Anklet(0, 1, 2))
        >>> g.is_biconnected()
        True
        >>> g.clear_hyperedges()
        >>> g.add_hyperedges_from([Anklet(0, 1, 2), Anklet(0, 1, 3)])
        >>> g.is_biconnected()
        True
        >>> g.clear_hyperedges()
        >>> g.add_hyperedges_from([Anklet(0, 1, 2), Anklet(0, 3, 4)])
        >>> g.is_biconnected()
        False
        """
        return nx.is_biconnected(self.to_adjacency_graph())

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Reduction
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def reduce(self) -> None:
        """Remove hyperedge which have no bearing on anklet graph equality.

        First, all hyperedges of length `n ≤ 1` are removed.
        Next, each hyperedge of length `n = 2` is either removed or has its multiplicity set to one;
        those whose two elements appear adjacent in another hyperedge are removed.
        All hyperedges of length `≥ 3` are left unaltered.

        Examples
        --------
        >>> g = AnkletGraph()
        >>> g.add_hyperedges_from(
        ...     {Anklet(0): 2, Anklet(0, 1): 3, Anklet(1, 2): 4, Anklet(1, 2, 3): 2}
        ... )
        >>> g.reduce()
        >>> g.hyperedges
        ((A(0, 1), 1), (A(1, 2, 3), 2))
        """
        if self._reduced:
            # The graph has previously been determined to be reduced (either by calling this method
            # or removing all hyperedges) and since then no reduction-spoiling
            # operations have been performed: no need to do anything
            return

        # Remove hyperedges of length ≤ 1
        self._edge = {hype: k for hype, k in self._edge.items() if len(hype) > 1}

        def adjacent_pair(x: T, y: T, a: Anklet[T]) -> bool:
            """Determine if `x` and `y` appear adjacent in the bracelet `a`."""
            try:
                i = a.index(x)
                j = a.index(y)
                return abs(i - j) == 1 or (0, len(a) - 1) in [(i, j), (j, i)]
            except ValueError:
                # Either x or y is not in the anklet
                return False

        # For each hyperedge of length 2 either remove entirely or set multiplicity to one
        for hype in list(self._edge):
            if len(hype) == 2:
                if any(
                    adjacent_pair(hype[0], hype[1], hype2)
                    for hype2 in self._edge
                    if hype2 is not hype
                ):
                    self._edge.pop(hype)
                else:
                    self._edge[hype] = 1

        # Record that the graph has been reduced
        self._reduced = True

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Partial order
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def __le__(self, other: object) -> NotImplementedType | bool:
        """Return whether the anklet graph embeds into another anklet graph.

        An anklet graph *g* embeds into an anklet graph *h* if the nodes of *g* are a subset of the
        nodes of *h* and there exists an embedding of the non-trivial (length > 1) hyperedges 
        of *g* into the hyperedges of *h* such that the images of the hyperedges do not cross.

        Parameters
        ----------
        other : object
            An anklet graph.

        Returns
        -------
        NotImplementedType or bool
            Returns `NotImplemented` if `other` is not an anklet graph.
            Otherwise, returns whether there exists an embedding of the anklet graph into `other`.
        """
        if not isinstance(other, AnkletGraph):
            return NotImplemented

        if not set(self._node) <= set(other._node):
            return False

        # Collect lists of all non-trivial hyperedges, with multiplicity
        hypes_s = [hype for hype in self._all_hyperedges() if len(hype) > 1]
        hypes_o = [hype for hype in other._all_hyperedges() if len(hype) > 1]

        # Build a graph where the nodes are all pairs of indices (i, j)
        # for which hypes_s[i] is a subanklet of hypes_o[j] (see Anklet.__le__)
        g = nx.Graph()
        for i, hype_s in enumerate(hypes_s):
            new_nodes = [(i, j) for j, hype_o in enumerate(hypes_o) if hype_s <= hype_o]
            if not new_nodes:
                # This individual hyperedge cannot embed into *any* hyperedges of 'other'
                return False
            g.add_nodes_from(new_nodes)

        # Add an edge between (i1, j1) and (i2, j2) if the embedding of hyperedges i1 and i2
        # of 'self' can embed into the hyperedges j1 and j2 of 'other' simultaneously without
        # crossing. This requires i1 != i2 (else one is assigning two embeddings to only
        # one hyperedge) and then either j1 != j2 or checking Anklet.noncrossing for embedding
        # two hyperedges of 'self' into the same hyperedge of 'other'
        for (i1, j1), (i2, j2) in combinations(g, 2):
            if i1 != i2 and (j1 != j2 or hypes_o[j1].noncrossing(hypes_s[i1], hypes_s[i2])):
                g.add_edge((i1, j1), (i2, j2))

        # Find the size of the largest clique (weight=None for all node weights equal to 1).
        # If it matches the number of hyperedges of 'self' that means that there is a choice
        # of embedding for all hyperedges which ensures they pair-wise don't cross
        _, clique_size = nx.max_weight_clique(g, weight=None)  # type: ignore
        return clique_size == len(hypes_s)

    def __lt__(self, other: object) -> NotImplementedType | bool:
        """Return whether `self <= other` and not `other <= self`.

        See :meth:`__le__` for the definition of the underlying relation on anklet graphs.
        """
        if not isinstance(other, AnkletGraph):
            return NotImplemented
        return self <= other and not other <= self

    def __ge__(self, other: object) -> NotImplementedType | bool:
        """Return whether `other <= self`.

        See :meth:`__le__` for the definition of the underlying relation on anklet graphs.
        """
        if not isinstance(other, AnkletGraph):
            return NotImplemented
        return other <= self

    def __gt__(self, other: object) -> NotImplementedType | bool:
        """Return whether `other <= self` and not `self <= other`.

        See :meth:`__le__` for the definition of the underlying relation on anklet graphs.
        """
        if not isinstance(other, AnkletGraph):
            return NotImplemented
        return other <= self and not self <= other

    def __eq__(self, other: object) -> NotImplementedType | bool:
        """Return whether `self <= other` and `other <= self`.

        See :meth:`__le__` for the definition of the underlying relation on anklet graphs.

        Two anklet graphs are equal if each embeds into the other. This clearly requires that they
        have the same set of nodes, but it does not mean that they have the same set of hyperedges.
        However, it *is* the case that two equal anklet graphs must have all hyperedges
        of length `n ≥ 3` in common.
        """
        if not isinstance(other, AnkletGraph):
            return NotImplemented
        return self <= other <= self
