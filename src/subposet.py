"""Methods for working for collections of path bi-graphs."""

from collections.abc import Sequence
from tqdm import tqdm
from padded_graphs import PathBiGraph


def remove_identical(graphs: Sequence[PathBiGraph]) -> list[PathBiGraph]:
    """Filter out identical path bi-graphs
    (as determined by comparing the output of :meth:`PathBiGraph.data_string`).
    """
    return list({g.data_string(): g for g in graphs}.values())


def unique_elements(graphs: Sequence[PathBiGraph], *, progress: bool = False) -> list[PathBiGraph]:
    """Return unique elements from a collection of path bi-graphs."""
    unique_graphs = []
    graph_iter = remove_identical(graphs)
    if progress:
        graph_iter = tqdm(graph_iter, desc="finding unique elements (0)", ascii=True)
    for g in graph_iter:
        if not any(g == g2 for g2 in unique_graphs):
            unique_graphs.append(g)
            if isinstance(graph_iter, tqdm):
                graph_iter.set_description(f"finding unique elements ({len(unique_graphs)})")
    return unique_graphs


def minimal_elements(graphs: Sequence[PathBiGraph], *, progress: bool = False) -> list[PathBiGraph]:
    """Return minimal elements from a collection of path bi-graphs.

    All path bi-graphs must have the same number of left and right nodes and no center nodes.
    """

    if not graphs:
        return []

    for g in graphs:
        if g.n_center != 0:
            raise ValueError("graph has center nodes")
        if (g.n_left, g.n_right) != (graphs[0].n_left, graphs[0].n_right):
            raise ValueError("graphs do not all have the same number of left/right nodes")

    graph_iter = remove_identical(graphs)
    if progress:
        graph_iter = tqdm(graph_iter, desc="finding minimal elements (0)", ascii=True)
    minimal_graphs = []
    for g in graph_iter:
        if not any(g_minimal <= g for g_minimal in minimal_graphs):
            minimal_graphs = [g_minimal for g_minimal in minimal_graphs if not g <= g_minimal]
            minimal_graphs.append(g)
            if isinstance(graph_iter, tqdm):
                graph_iter.set_description(f"finding minimal elements ({len(minimal_graphs)})")

    return minimal_graphs
