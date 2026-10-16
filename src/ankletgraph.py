"""Anklet graphs."""

from collections.abc import Collection, Hashable, Iterable, Iterator, Mapping
from typing import Any
import networkx as nx
from anklet import Anklet


class AnkletGraph[T: Hashable]:
    """An **anklet graph** is a multi-hypergraph with additional combinatorial structure.

    A hyperedge in an anklet graph is represented by a finite sequence of unique incident nodes
    considered up to cyclic rotation and reversal: an *anklet*. That is, each hyperedge specifies
    a cylic ordering of its incidences with no chosen orientation or distinguished starting point.

    Forgetting the anklet structure of the hyperedges yields an ordinary multi-hypergraph:
    each hyperedge is simply incident to the set of nodes appearing in its sequence.

    An embedding of an anklet graph into a surface must preserve the anklet structure of its
    hyperedges. This means that a hyperedge of size `n` must be embedded as a topological disk
    whose boundary is subdivided into an `n`-gon with the incident nodes appearing at the vertices
    in the prescribed cyclic order.
    """

    _name: str
    _attr: dict[str, Any]
    _node: dict[T, dict[str, Any]]
    _edge: dict[Anklet[T], int]

    def __init__(self, nodes: Iterable[T] = (), *, name: str = "", **attr: Any) -> None:
        self._name = name
        self._attr = attr
        self._node = {}
        self._edge = {}

        self.add_nodes_from(nodes)

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
        >>> print(g)
        AnkletGraph named myGraph with attribute(s) (color, type), 5 nodes and 0 hyperedges
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

        See Also
        --------
        :meth:`get_attribute`,
        :meth:`set_attributes`,
        :meth:`remove_attribute`
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
        """Remove a node."""
        raise NotImplementedError()

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

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Incidence / adjacency
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def incidence(self) -> dict[T, Anklet[T]]:
        """Return the incidence data of the graph."""
        raise NotImplementedError()

    def adjacency(self) -> dict[T, set[T]]:
        """Return the adjacency data of the graph."""
        raise NotImplementedError()

    def connected_components(self) -> Iterator[set[T]]:
        """Generate connected components."""
        return nx.connected_components(self.to_undirected())

    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--
    #   Associated graphs
    # ==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--~~==~~--

    def to_undirected(self) -> nx.Graph:
        """The simple graph reflecting node adjacencies in the anklet graph."""
        raise NotImplementedError()

    def skeleton_graph(self) -> nx.MultiGraph:
        """The multi-graph formed by replacing each hyperedge by a cycle."""
        raise NotImplementedError()

    def wheel_graph(self) -> nx.MultiGraph:
        """The multi-graph formed by replacing each hyperedge by a wheel."""
        raise NotImplementedError()
