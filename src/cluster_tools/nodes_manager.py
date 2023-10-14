from ..cli_director import CLI_director


def cli_mode(hosts, nodes, cluster_info) -> None:
    """
    Launching CLI node.

    :param hosts:
    :type hosts:
    :param nodes:
    :type nodes:
    :param cluster_info:
    :type cluster_info:
    """
    cli_director = CLI_director(hosts, nodes, cluster_info)
    cli_director.cmdloop()
