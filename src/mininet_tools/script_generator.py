from typing import Dict, List, Union, Any

from config import SCRIPT_FOLDER_PATH
from src.cluster_tools import get_next_ip
from src.mininet_tools.host_configurator import define_node_ip_pool
from src.mininet_tools.ns_script_template import gen_mn_ns_script_by_template_with_custom_host_ip


def generate_mn_ns_script_with_custom_host_ip_auto(
    nodes: Dict[str, Dict[str, str]],
    groups: Dict[str, Dict[str, List[Union[str, int]]]],
    leaves: List[int],
    hosts_net_services: Any,
) -> Dict[str, Dict[str, str]]:
    """
    Generate turn on script for Cluster node.

    :param nodes:
    :type nodes: Dict[str, Dict[str, str]]
    :param groups:
    :type groups: Dict[str, Dict[str, List[Union[str, int]]]]
    :param leaves: List of indexes leave-nodes in graph.
    :type leaves: List[int]
    :param hosts_net_services:
    :type hosts_net_services: Any

    :return: Dict of hosts data
    :rtype: Dict[str, Dict[str, str]]
    """

    hosts = {}
    nodes = define_node_ip_pool(groups, leaves, nodes)

    for ip, node in nodes.items():
        group = groups[node["group"]]
        curr_host_ip = node["IP_pool"]
        for node_in_gr in group["vertexes"]:
            if node_in_gr in leaves:
                curr_host = "h" + str(node_in_gr)
                host = {"IP": curr_host_ip, "name": curr_host, "IP_node": ip}

                hosts[curr_host] = host
                curr_host_ip = get_next_ip(curr_host_ip)

        filepath = f"{SCRIPT_FOLDER_PATH}turn_on_script_for_{ip}.py"
        print(f"HOSTS: {hosts}")
        with open(filepath, "w") as file:
            spec_group = groups["no_group"]

            gen_mn_ns_script_by_template_with_custom_host_ip(
                file, node, group, spec_group, leaves, hosts_net_services, hosts
            )

    return hosts
