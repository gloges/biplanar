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
