from typing import Dict, Any, Tuple, List
import networkx as nx

from config import NODELIST_FILE_PATH
from src.ktreads import KThread


def read_nodelist_from_file(nodelist_filepath: str = NODELIST_FILE_PATH) -> Dict[str, Dict[str, Any]]:
    """
    Read list of cluster nodes from file.

    :param nodelist_filepath: Name of file with list of cluster nodes.
    :type nodelist_filepath: str

    :return: list of cluster nodes.
    :rtype: Dict[str, Dict[str, Any]]
    """

    nodes = {}
    with open(nodelist_filepath, "r") as nodelist_file:
        for i, file_line in enumerate(nodelist_file):
            if not file_line.strip() or file_line.startswith("#"):
                continue

            split_line = file_line.split(" ")
            nodes[split_line[0]] = {
                "IP": split_line[0],
                "hostname": split_line[1],
                "username": split_line[2],
                "out_intf": split_line[3],
                "controller": (
                    split_line[4],
                    split_line[5].strip(),
                ),
                "group": i,
                "IP_pool": None,
                "ssh": None,
                "ssh_chan": None
            }

    return nodes


def get_networkx_graph(graph_data: Any) -> Tuple[nx.Graph, Dict[int, List[int]], Any]:
    """
    Generate networkX graph from JSON string.

    :param graph_data: Json string, that describes graph.
    :type graph_data: Any

    :return:
    :rtype: Tuple[networkx.Graph, Dict[int, List[int]], Any]
    """
    graph = nx.Graph()
    pos = {}
    for edge in graph_data["edges"]:
        if int(edge[0]) not in graph.nodes():
            graph.add_node(int(edge[0]))
            pos[int(edge[0])] = [
                graph_data["pos"][edge[0]][0],
                0 - graph_data["pos"][edge[0]][1],
            ]

        if int(edge[1]) not in graph.nodes():
            graph.add_node(int(edge[1]))
            pos[int(edge[1])] = [
                graph_data["pos"][edge[1]][0],
                0 - graph_data["pos"][edge[1]][1],
            ]

        graph.add_edge(int(edge[0]), int(edge[1]))
    return graph, pos, graph_data["netapps"]


def get_next_ip_pool(IP: str, hosts_number: int) -> str:
    """
    Generate the first IP address on next IP address pool. Depends on IP address pool size.

    :param IP: The first address of current pool.
    :type IP: str
    :param hosts_number: The size of current pool.
    :type hosts_number: int

    :return: The first IP address of the next pool. The input and output IP addresses are strings.
    :rtype: str
    """
    octets = IP.split(".")
    if int(octets[3]) + hosts_number >= 255:
        new_oct = divmod(int(octets[3]) + hosts_number, 255)
        next_ip_pool = (
                octets[0]
                + "."
                + octets[1]
                + "."
                + str(int(octets[2]) + int(new_oct[0]))
                + "."
                + str(int(new_oct[1]) + int(new_oct[0]))
        )
    else:
        next_ip_pool = (
                octets[0]
                + "."
                + octets[1]
                + "."
                + str(int(octets[2]))
                + "."
                + str(int(octets[3]) + hosts_number)
        )
    return next_ip_pool


def get_next_ip(ip: str) -> str:
    """
    Generate the next IP address by incrementing the last octet of the current IP address.

    :param ip: The current IP address in the format 'x.x.x.x'.
    :type ip: str
    :return: The next incremented IP address in the format 'x.x.x.x'.
    :rtype: str
    """
    octets = ip.split(".")
    if int(octets[3]) + 1 >= 255:
        next_ip = (
                octets[0] + "." + octets[1] + "." + str(int(octets[2]) + 1) + "." + "1"
        )
    else:
        next_ip = (
                octets[0]
                + "."
                + octets[1]
                + "."
                + octets[2]
                + "."
                + str(int(octets[3]) + 1)
        )
    return next_ip


def make_threaded(function: callable, args: List[Any], nodes: Dict[str, Dict[str, str]]) -> None:
    """
    Launch a function in threads, where the number of threads is equal to the number of cluster nodes.

    :param function: The function to be executed in each thread.
    :type function: callable
    :param args: Arguments to be passed to the function.
    :type args: List[Any]
    :param nodes: Dictionary representing the cluster nodes map.
    :type nodes: Dict[str, Dict[str, str]]
    """
    threads = []
    t_args = tuple(args)
    for node_label in nodes:
        thread_args = (node_label,) + t_args
        thread = KThread(target=function, *thread_args)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
