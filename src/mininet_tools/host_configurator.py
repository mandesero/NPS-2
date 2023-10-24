from typing import Dict, List, Union, Any

from config import FIRST_HOST_IP, BASE_INTERFACE
from src.cluster_tools import get_next_ip_pool, get_next_ip
from src.cluster_tools.mininet_cmd_manager import send_mininet_cmd_to_cluster_node


def define_node_ip_pool(
        groups: Dict[str, Dict[str, List[Union[str, int]]]],
        leaves: List[int],
        nodes: Dict[str, Dict[str, str]],
) -> Dict[str, Dict[str, str]]:
    """
    Defines the cluster node pool based on number of hosts and switches on concrete cluster node.

    :param nodes:
    :type nodes: Dict[str, Dict[str, str]]
    :param groups:
    :type groups: Dict[str, Dict[str, List[Union[str, int]]]]
    :param leaves: List of indexes leave-nodes in graph.
    :type leaves: List[int]

    :return: nodes
    :rtype: Dict[str, Dict[str, str]]

    Note:
        make not executable get_next_IP_pool on last iteration
    """

    next_ip_pool = FIRST_HOST_IP

    n = len(nodes.values()) - 1
    for i, node in enumerate(nodes.values()):
        group = groups[node["group"]]
        host_num = len(group["vertexes"])
        for node_in_gr in group["vertexes"]:
            if node_in_gr not in leaves:
                host_num -= 1
        node["IP_pool"] = next_ip_pool
        if i != n:
            next_ip_pool = get_next_ip_pool(next_ip_pool, host_num)
    return nodes


def host_process_configurator_nodegroup(node, groups, CIDR_mask, leaves, hosts):
    """Configurate hosts processes network interfaces in each nodegroup.

    :param node:
    :type node:
    :param groups:
    :type groups:
    :param CIDR_mask: CIRD mask of IP address for host network interface.
    :type CIDR_mask:
    :param leaves: List of leave-nodes in network graph.
    :type leaves:
    :param hosts:
    :type hosts:
    """
    first_host_ip = node["IP_pool"]
    curr_host_ip = first_host_ip
    group = groups[node["group"]]
    for vertex in group["vertexes"]:
        if vertex in leaves:
            # reset config on host interface
            curr_host = "h" + str(vertex)
            cmd = curr_host + " ifconfig " + curr_host + f"-{BASE_INTERFACE} 0"
            send_mininet_cmd_to_cluster_node(node, cmd)
            # config new IP address on host interface
            cmd = (
                    curr_host
                    + " ifconfig "
                    + curr_host
                    + f"-{BASE_INTERFACE} "
                    + curr_host_ip
                    + "/"
                    + CIDR_mask
            )
            send_mininet_cmd_to_cluster_node(node, cmd)

            host = {
                "nodeIP": node["IP"],
                "name": curr_host,
                "IP": curr_host_ip
            }
            hosts[curr_host] = host

            # prepare for next host
            curr_host_ip = get_next_ip(curr_host_ip)
