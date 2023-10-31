from copy import deepcopy
from typing import Dict, List, Union, Tuple

import networkx as nx
import metis


def split_graph_on_parts(nx_graph: nx.Graph, nodes: Dict[str, Dict[str, str]]):
    """Split graph on sub-graphs.

    :param nx_graph:
    :type nx_graph: networkx.Graph
    :param nodes:
    :type nodes: Dict[str, Dict[str, str]]

    """
    number_of_parts = len(nodes)

    if number_of_parts == 1:
        (edgecuts, parts) = metis.part_graph(nx_graph, number_of_parts, recursive=True)
    else:
        (edgecuts, parts) = metis.part_graph(
            nx_graph, number_of_parts, contig=True, compress=True
        )

    node_ids = {i: id for i, id in enumerate(nx_graph.nodes())}

    groups = {}
    for p in set(parts):
        group = {}
        group["vertexes"] = []
        group["edges"] = []
        groups[p] = group

    for i, p in enumerate(parts):
        groups[p]["vertexes"].append(node_ids[i])  # test

    special_group = {}
    special_group["vertexes"] = []
    special_group["edges"] = []
    groups["no_group"] = special_group

    for edge in nx_graph.edges():
        no_group_flag = True
        for id, group in groups.items():
            if (edge[0] in group["vertexes"]) and (edge[1] in group["vertexes"]):
                group["edges"].append(edge)
                no_group_flag = False
                break
        if no_group_flag:
            group = groups["no_group"]
            group["edges"].append(edge)
            if edge[0] not in group["vertexes"]:
                group["vertexes"].append(edge[0])
            if edge[1] not in group["vertexes"]:
                group["vertexes"].append(edge[1])

    for key, node in list(nodes.items()):
        if node["group"] not in set(parts):
            del nodes[key]

    return groups, nodes


def define_leaves_in_graph(nx_graph: nx.Graph) -> List[int]:
    """
    Create list of indexes leave-nodes in graph.

    :param nx_graph: Graph.
    :type nx_graph: networkx.Graph

    :return: List of idx leave-nodes.
    :rtype: List[int]
    """
    return [key for key, val in nx.degree(nx_graph) if val == 1]
