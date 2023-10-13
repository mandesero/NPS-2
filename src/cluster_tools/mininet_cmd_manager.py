import sys


def send_mininet_cmd_to_cluster_node(node, cmd, quite=True):
    """Send Mininet console command to cluster node.

    :param node: IP address of cluster node.
    :type node:
    :param cmd: Console command scripts.
    :type cmd:
    :param quite:
    :type quite:
    """

    cmd += "\n"
    node["ssh_chan"].send(cmd)
    buff = ""
    if cmd != "exit\n":
        last = ""
        while not buff.endswith("mininet> "):
            out = node["ssh_chan"].recv(1)
            if out:
                if out == "\n" and last == "\n":  # remove duplication end of line
                    pass
                elif not quite:
                    sys.stdout.write(out)
            buff += out
            last = out


def send_mininet_ping_to_cluster_node(node, cmd):
    """Send Mininet console command PING to cluster node and check the result of its execution.

    :param node: IP address of cluster node.
    :type node:
    :param cmd: Console command scripts.
    :type cmd:

    # :return:
    #     True - If the ping reached the destination point successfully.
    #     False - If the ping failed to reach the destination point.
    # :rtype: bool
    """
    cmd += "\n"
    node["ssh_chan"].send(cmd)
    buff = ""
    last = ""
    while not buff.endswith("mininet> "):
        out = node["ssh_chan"].recv(1)
        if out:
            if out == "\n" and last == "\n":  # remove duplication end of line
                pass
            else:
                sys.stdout.write(out)
        buff += out
        last = out
