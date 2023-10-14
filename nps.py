import json
from time import time
from typing import Any

import loguru
import networkx as nx
from matplotlib import pyplot as plt
from paramiko.util import log_to_file

from config import *
from src.cluster_tools import read_nodelist_from_file, get_networkx_graph, make_threaded, cli_mode, \
    send_mininet_cmd_to_cluster_node
from src.cluster_tools.ssh_manager import open_ssh_to_node, close_ssh_to_nodes
from src.cluster_tools.cmd_manager import send_support_scripts_to_cluster_node, \
    send_cmd_to_cluster_node, exec_start_up_script
from src.mininet_tools import split_graph_on_parts, define_leaves_in_graph, \
    generate_mn_ns_script_with_custom_host_ip_auto
from src.mininet_tools.host_configurator import host_process_configurator_nodegroup


class NPS:
    logger = loguru.logger
    begin_config_ts: float
    pos: Any = None
    nodes: dict = {}
    hosts: dict = {}
    groups: dict = {}
    cluster_info: dict = {}
    input_file_path: str

    def __init__(self, file_path: str = GRAPH_FILE_PATH):
        self.logger.add(NPS_LOG_PATH, level="INFO")
        self.begin_config_timestamp = time()
        self.input_file_path = file_path
        log_to_file(PARAMIKO_LOG_PATH)
        self.logger.info("NPS INIT")

    def start(self):
        self.logger.info("Start...")

        self.nodes = read_nodelist_from_file()
        self.logger.info("Take cluster nodes...")

        if os.path.isfile(self.input_file_path):
            with open(self.input_file_path, "r") as graph_file:
                graph_data = json.loads(graph_file.read())
        else:
            self.logger.error(f"FileNotFoundError: No such file or directory: {self.input_file_path}")
            exit()

        self.logger.info("Init graph...")

        if DRAWING_FLAG:
            nx_graph, self.pos, node_services = get_networkx_graph(graph_data)
            if SAVE_GRAPH_FIG_FLAG:
                nx.draw(nx_graph, pos=self.pos)
                plt.savefig("graph.jpg")
        else:
            nx_graph, _, node_services = get_networkx_graph(graph_data)

        self.logger.info("Create networkx.Graph...")

        leaves = define_leaves_in_graph(nx_graph)
        self.logger.info("Define leaves nodes...")

        self.groups, self.nodes = split_graph_on_parts(
            nx_graph, self.nodes
        )

        self.logger.info("Split network graph to clusters...")

        with open(GROUPS_FILE_PATH, "w") as groups_file:
            groups_file.write(str(json.dumps(self.groups)))

        self.logger.info("Write info about graph groups...")

        self.hosts = (
            generate_mn_ns_script_with_custom_host_ip_auto(
                self.nodes, self.groups, leaves, node_services
            )
        )
        self.logger.info("Generate start up scripts for Mininet nodes...")

        with open(HOSTS_FILE_PATH, "w") as hosts_file:
            hosts_file.write(str(json.dumps(self.hosts)))

        self.logger.info("Write info about hosts...")

        make_threaded(open_ssh_to_node, [], self.nodes)
        self.logger.info("Open SSH to all nodes in cluster...")

        make_threaded(send_support_scripts_to_cluster_node, [], self.nodes)
        self.logger.info("Send scripts to nodes...")

        if MALWARE_MODE_ON:
            # Turn ON infected hosts file monitor scripts on cluster nodes
            file_monitor_cmd = (
                    "python "
                    + DST_SCRIPT_FOLDER
                    + "file_monitor.py "
                    + MALWARE_CENTER_IP
                    + " "
                    + str(MALWARE_CENTER_PORT)
                    + " "
                    + DST_SCRIPT_FOLDER
                    + INFECTED_HOSTS_FILENAME
                    + " &"
            )
            make_threaded(
                send_cmd_to_cluster_node,
                [
                    file_monitor_cmd,
                ],
                self.nodes,
            )
            self.logger.info("Turn ON file monitor scripts on nodes...")

        make_threaded(exec_start_up_script, [], self.nodes)
        self.logger.info("Execute start up scripts on nodes...")

        make_threaded(
            host_process_configurator_nodegroup,
            [self.groups, str(HOST_NETMASK), leaves, self.hosts],
            self.nodes,
        )

        self.logger.info("Configure host-processes eth interfaces."),
        end_config_timestamp = time()
        self.logger.info(f"Setting up cluster for {end_config_timestamp - self.begin_config_timestamp} sec.")

        # Simulation clusters step

        if CLI_MODE:
            self.cluster_info["switch_number"] = len(
                set(nx_graph.nodes()).difference(set(leaves))
            )
            node_info = {}
            for _id, group in self.groups.items():
                if _id != "no_group":
                    h_num = len(set(group["vertexes"]).intersection(leaves))
                    sw_num = len(group["vertexes"]) - h_num
                    node_info[_id] = (h_num, sw_num)
            self.cluster_info["node_info"] = node_info
            cli_mode(self.hosts, self.nodes, self.cluster_info)
            self.logger.info("Turn OFF CLI interface...")

        # Shutdown all cluster nodes.
        make_threaded(
            send_mininet_cmd_to_cluster_node,
            [
                "exit",
            ],
            self.nodes,
        )
        self.logger.info("Shutdown all cluster nodes. Sending exit to Mininet on nodes..."),

        make_threaded(
            send_cmd_to_cluster_node,
            [
                "ovs-vsctl list-br | xargs -L1 ovs-vsctl del-br",
            ],
            self.nodes,
        )
        self.logger.info("Deleting OVS bridges from cluster nodes..."),

        make_threaded(
            send_cmd_to_cluster_node,
            [
                "exit",
            ],
            self.nodes,
        )
        close_ssh_to_nodes(self.nodes)
        self.logger.info("Close SSH session to all nodes in cluster..."),
        self.logger.info("Finish simulating...")

    def clean(self):
        self.nodes = read_nodelist_from_file(NODELIST_FILE_PATH)
        self.logger.info(f"Take cluster nodes...")

        make_threaded(open_ssh_to_node, [], self.nodes)
        self.logger.info("Open SSH to all nodes in cluster..."),

        make_threaded(
            send_cmd_to_cluster_node,
            [
                "ovs-vsctl list-br | xargs -L1 ovs-vsctl del-br",
            ],
            self.nodes,
        )
        self.logger.info("Deleting OVS bridges from cluster nodes..."),

        make_threaded(
            send_cmd_to_cluster_node,
            [
                "exit",
            ],
            self.nodes,
        )
        close_ssh_to_nodes(self.nodes)
        self.logger.info("Close SSH session to all nodes in cluster..."),
        self.logger.info("Clean done...")
        exit(0)
