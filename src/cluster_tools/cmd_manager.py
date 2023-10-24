from typing import Dict, Any

from paramiko import Transport
from paramiko.sftp_client import SFTPClient

from config import SRC_SCRIPT_FOLDER, DST_SCRIPT_FOLDER, INFECTED_HOSTS_FILENAME


def send_script_to_cluster_node(node: Dict[str, str], script_filename: str) -> None:
    """
    Send file with python script to cluster node.

    :param node: node of network
    :type node: Dict[str, str]
    :param script_filename: Name of script file. File on Cluster Manager machine and on cluster node machine will have
    the same name.
    :type script_filename: str
    """
    # open SFTP session to node
    transport = Transport((node["IP"], 22))
    transport.connect(username=node["username"], password=node["username"])
    sftp = SFTPClient.from_transport(transport)

    # config script file paths
    src_script_filepath = SRC_SCRIPT_FOLDER + script_filename
    dst_script_filepath = DST_SCRIPT_FOLDER + script_filename

    # send script via SFTP
    sftp.put(src_script_filepath, dst_script_filepath)

    # close SFTP session to node
    sftp.close()
    transport.close()


def send_support_scripts_to_cluster_node(node: Dict[str, str]) -> None:
    """
    Send helpful scripts to cluster nodes.
    This scripts used in malware propagation experiment ONLY!

    :param node: node of network
    :type node: Dict[str, str]
    """

    # delete old scripts
    del_old_support_scripts_cmd = f"rm {DST_SCRIPT_FOLDER} *"
    send_cmd_to_cluster_node(node, del_old_support_scripts_cmd)

    script_name = f"turn_on_script_for_{node['IP']}.py"
    send_turn_on_script_to_cluster_node(node, script_name)
    send_script_to_cluster_node(node, "scapy_packet_gen.py")
    send_script_to_cluster_node(node, "port_sniffer.py")
    send_script_to_cluster_node(node, "file_monitor.py")
    send_script_to_cluster_node(node, "worm_instance.py")


def send_turn_on_script_to_cluster_node(node: Dict[str, str], script_filename: str) -> None:
    """
    Send start up script to cluster node.

    This script generated for each cluster node specially. The generation algorithm depends on mapping
    of simulated topology on cluster topology.

    :param node: node of network
    :type node: Dict[str, str]
    :param script_filename: Name of script file. File on Cluster Manager machine and on cluster node machine will
    have the same name.
    :type script_filename: str
    """
    # open SFTP session to node
    transport = Transport((node["IP"], 22))
    transport.connect(username=node["username"], password=node["username"])
    sftp = SFTPClient.from_transport(transport)

    # config script file paths
    src_script_filepath = f"{SRC_SCRIPT_FOLDER}nodes/{script_filename}"
    dst_script_filepath = DST_SCRIPT_FOLDER + script_filename

    # send script via SFTP
    sftp.put(src_script_filepath, dst_script_filepath)

    # close SFTP session to node
    sftp.close()
    transport.close()


def send_cmd_to_cluster_node(node: Dict[str, Any], cmd: str) -> None:
    """
    Send a console command to a cluster node.

    :param node: Dictionary representing the cluster node with its IP address and SSH channel.
    :type node: Dict[str, str]
    :param cmd: The console command script to be sent.
    :type cmd: str
    """

    cmd += "\n"
    node["ssh_chan"].send(cmd)
    if cmd != "exit\n":
        buff = ""
        endswith_str = "root@" + node["hostname"] + ":~# "
        while not buff.endswith(
                endswith_str
        ):  # Need to change name, or use the variable.
            buff += node["ssh_chan"].recv(9999).decode()


def exec_start_up_script(node: Dict[str, str]) -> None:
    """
    Send the console command to cluster Node to execute the start-up script.

    :param node: Dictionary representing the cluster node with its IP address and SSH channel.
    :type node: Dict[str, str]
    """

    reset_vs_db_cmd = "ovs-vsctl list-br | xargs -L1 ovs-vsctl del-br"
    send_cmd_to_cluster_node(node, reset_vs_db_cmd)

    # Flush options on eth1 interface on nodes in cluster. This interface will be used for inter
    # Mininet instances communications
    reset_intf_cmd = "ifconfig " + node["out_intf"] + " 0"
    send_cmd_to_cluster_node(node, reset_intf_cmd)

    split_ip = node["IP"].split(".")
    reset_vs_cmd = "ovs-vsctl del-br s" + split_ip[3]
    send_cmd_to_cluster_node(node, reset_vs_cmd)

    clean_infected_hosts_file_cmd = "> " + DST_SCRIPT_FOLDER + INFECTED_HOSTS_FILENAME
    send_cmd_to_cluster_node(node, clean_infected_hosts_file_cmd)

    # Turn On Mininet instance on nodes in cluster
    send_mn_turn_on_cmd_to_cluster_node(node)


def send_mn_turn_on_cmd_to_cluster_node(node: Dict[str, Any]) -> None:
    """
    Send the console command to cluster node to start up the Mininet.

    :param node: Dictionary representing the cluster node with its IP address and SSH channel.
    :type node: Dict[str, str]
    """
    turn_on_mininet_script_name = "turn_on_script_for_" + node["IP"] + ".py"
    cmd = "python " + DST_SCRIPT_FOLDER + turn_on_mininet_script_name
    cmd += "\n"
    node["ssh_chan"].send(cmd)
    buff = ""
    while not buff.endswith("mininet> "):
        buff += node["ssh_chan"].recv(9999).decode()
