"""Methods for working with the BalloonGraph posets."""

from collections.abc import Hashable, Sequence
from itertools import combinations, product
import warnings
import networkx as nx
import numpy as np
from numpy import typing as npt
from tqdm import tqdm
from .balloon_graph import BalloonGraph


def compare_all[T: Hashable](graphs: Sequence[BalloonGraph[T]]) -> npt.NDArray[np.bool_]:
    """Return a square boolean array with all pair-wise comparisons of the balloon graphs.

    Element `(i, j)` of the returned array is equal to `graphs[i] <= graphs[j]`.
    """
    poset_matrix = np.empty([len(graphs), len(graphs)], dtype=bool)
    for (i, gi), (j, gj) in tqdm(
        product(enumerate(graphs), repeat=2),
        total=len(graphs)**2,
        desc=f"Comparing {len(graphs)} graphs in pairs",
        ascii=True,
    ):
        poset_matrix[i][j] = gi <= gj
    return poset_matrix


def get_poset_dag(poset_matrix: npt.NDArray[np.bool_]) -> nx.DiGraph:
    """Return the transitively-reduced DAG constructed from the dense array of comparisons."""
    rows, cols = poset_matrix.shape
    if rows != cols:
        raise ValueError(f"poset_matrix (shape = {poset_matrix.shape}) is not square")

    poset_dag = nx.DiGraph()
    poset_dag.add_nodes_from(range(rows))
    for i, j in combinations(range(rows), r=2):
        if i not in poset_dag or j not in poset_dag:
            continue
        if poset_matrix[i][j] and poset_matrix[j][i]:
            warnings.warn(
                f"rows {i} and {j} are equal. removing node {j} from the DAG",
                UserWarning
            )
            poset_dag.remove_node(j)
        elif poset_matrix[i][j]:
            poset_dag.add_edge(i, j)
        elif poset_matrix[j][i]:
            poset_dag.add_edge(j, i)

    return nx.transitive_reduction(poset_dag)


def standard_order(graphs: Sequence[BalloonGraph], poset_dag: nx.DiGraph) -> list[int]:
    """Return a topological sort of the graphs.

    The sort is such that the graph layers (smallest distance from the minimal graph)
    are weakly increasing. Within each layer the graphs are sorted into according to number
    of balloons, number of anklet graphs, etc. so that similar graphs appear together.

    For each graph its layer index and index within the layer are saved as attributes.
    """
    order = []

    for layer_index, layer in enumerate(nx.topological_generations(poset_dag)):
        layer_order = sorted(
            layer,
            key=lambda i: (
                graphs[i].number_of_balloons(),
                graphs[i].number_of_anklet_graphs(),
                sum(ag.number_of_unique_hyperedges() for _, ag in graphs[i].iter_anklet_graphs()),
                sum(ag.number_of_hyperedges() for _, ag in graphs[i].iter_anklet_graphs()),
                len(graphs[i].data_string()),
                graphs[i].data_string()
            )
        )
        order.extend(layer_order)
        for index, i in enumerate(layer_order):
            graphs[i].attributes = {'layer': layer_index, 'index': index}

    return order


def save_poset_data(
    folder: str,
    graphs: Sequence[BalloonGraph[int]],
    poset_matrix: npt.NDArray[np.bool_],
    order: list[int]
) -> None:
    """Save balloon graphs and the boolean array of their comparisons."""

    with open(folder + "/balloon_graphs.tsv", 'w', encoding='utf8') as file_out:
        for i in order:
            layer_index = graphs[i].attributes['layer']
            index = graphs[i].attributes['index']
            data = graphs[i].data_string()
            file_out.write(f"{layer_index}\t{index}\t{data}\n")

    np.savez(
        folder + "/poset_matrix.npz",
        data=np.packbits(poset_matrix[order][:, order]),
        shape=np.array(poset_matrix.shape),
    )


def load_poset_data(folder: str) -> tuple[list[BalloonGraph[int]], npt.NDArray[np.bool_]]:
    """Load balloon graphs and the boolean array of their comparisons."""

    # Load the balloon graphs, for each storing its layer and index as attributes
    graphs = []
    with open(folder + "/balloon_graphs.tsv", 'r', encoding='utf8') as file_in:
        for line in file_in.readlines():
            layer_index, index, data = line[:-1].split('\t')
            graph = BalloonGraph.from_data_string(data, int)
            graph.attributes = {'layer': int(layer_index), 'index': int(index)}
            graphs.append(graph)

    # Load and reconstruct the boolean array of comparisons
    with np.load(folder + "/poset_matrix.npz") as saved:
        shape = tuple(saved["shape"])
        size = int(np.prod(shape))
        poset_matrix = np.unpackbits(saved["data"], count=size).reshape(shape).astype(bool)

    return graphs, poset_matrix
