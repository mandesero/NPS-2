from paramiko.client import SSHClient, AutoAddPolicy
from typing import Dict, Any


def open_ssh_to_node(node: Dict[str, Any]) -> None:
    """
    Open SSH session to a specific node in the cluster.

    :param node: Dictionary representing the node with its IP, username, and password.
    :type node: Dict[str, str]

    """
    node["ssh"] = SSHClient()
    node["ssh"].set_missing_host_key_policy(AutoAddPolicy())
    node["ssh"].connect(
        hostname=node["IP"], username=node["username"], password=node["username"]
    )
    node["ssh_chan"] = node["ssh"].invoke_shell()


def open_ssh_to_nodes(node_map):
    """Open SSH sessions to each node in cluster.

    Args:
        node_map: Cluster nodes map.

    Returns:
        SSH session to cluster node map.
        SSH session chan to cluster node map.
    """
    ssh_map = {}
    ssh_chan_map = {}
    for node_IP in node_map.keys():
        ssh_map[node_IP] = SSHClient()
        ssh_map[node_IP].set_missing_host_key_policy(AutoAddPolicy())
        ssh_map[node_IP].connect(
            hostname=node_IP, username=node_map[node_IP], password=node_map[node_IP]
        )
        ssh_chan_map[node_IP] = ssh_map[node_IP].invoke_shell()

    return ssh_map, ssh_chan_map


def close_ssh_to_nodes(nodes: Dict[str, Dict[str, Any]]) -> None:
    """
    Close SSH sessions to all nodes in cluster.

    :param nodes: Dict contains cluster nodes.
    :type nodes: Dict[str, Dict[str, str]]
    """

    for node in nodes.values():
        node["ssh"].close()
