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

    All path bi-graphs must have the same number of east and west nodes.
    """

    if not graphs:
        return []

    for g in graphs:
        if (g.n_east, g.n_west) != (graphs[0].n_east, graphs[0].n_west):
            raise ValueError("graphs do not all have the same number of east/west nodes")

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


def sorted_data_strings(graphs: Sequence[PathBiGraph]) -> list[str]:
    """Return sorted data strings for a collection of path bi-graphs."""
    sort_data = []
    for g in graphs:
        bg_data = [
            (
                bg.number_of_balloons(),
                bg.number_of_anklet_graphs(),
                sum(ag.number_of_unique_hyperedges() for _, ag in bg.iter_anklet_graphs()),
                sum(ag.number_of_hyperedges() for _, ag in bg.iter_anklet_graphs()),
                len(bg.data_string())
            )
            for bg in g.balloon_graphs
        ]
        sort_data.append((*sorted(bg_data), g.data_string()))
    return [data_str for _, _, data_str in sorted(sort_data)]
