"""Methods for loading and saving collections of bigraphs."""

from collections.abc import Sequence
from padded_graphs import PathBiGraph


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


def save_path_bigraphs(file_path: str, graphs: Sequence[PathBiGraph]) -> None:
    """Write the data strings of a collection of path bi-graphs to the given file.

    Data strings are first sorted using :meth:`sorted_data_strings`.
    """
    with open(file_path, 'wt', encoding='utf-8') as file_out:
        for line in sorted_data_strings(graphs):
            file_out.write(line + '\n')


def load_path_bigraphs(file_path: str, n_east: int, n_west: int) -> list[PathBiGraph]:
    """Read in path bi-graphs from the given file."""
    graphs = []
    with open(file_path, 'rt', encoding='utf-8') as file_in:
        for line in file_in.readlines():
            data_g, data_h = line[1:-2].split('}, {')
            graphs.append(PathBiGraph(n_east, n_west, data_g, data_h))
    return graphs
