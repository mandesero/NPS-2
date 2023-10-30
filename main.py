import setup
from nps import NPS

# from shutil import copyfile
# from config import *

# def generate_mn_turn_on_script(
#         filepath,
#         nodes_ext_intf,
#         node_group,
#         edge_group,
#         ext_intf_list,
#         leaves,
#         node_ctrl_map,
#         hosts_net_services,
# ):
#     """Generate turn on script for Cluster node with network services.

#     Args:
#         filepath: Path to file.
#         nodes_ext_intf: Cluster node external network interface name.
#         node_group: Group ID to node-list map.
#         edge_group: Group ID to edge-list map.
#         ext_intf_list: External network interface name to the node group.
#         leaves: List of leave-node in network graph.
#     """
#     copyfile(TURN_ON_FILE_TEMPLATE_PATH, filepath)
#     sw_ext_intf_s = f"[{','.join(map(lambda node: f's{node}',ext_intf_list))}]"

#     # file.write('        "Add hosts and swiches"\n')
#     nodes_s = '\n'.join(
#         map(
#             lambda s: s.rjust(len(s) + 8, ' '),
#             map(
#                 lambda node: f"h{node} = self.addHost('h{node}')"\
#                 if node in leaves else f"s{node} = self.addSwitch('s{node}', protocols='OpenFlow13')",
#                 node_group
#             )
#         )
#     )

#     # file.write('        "Add links"\n')
#     links_s = '\n'.join(
#         map(
#             lambda s: s.rjust(len(s) + 8, ' '),
#             map(
#                 lambda edge: f"self.addLink({'h' if edge[0] in leaves else 's'}{edge[0]}, {'h' if edge[1] in leaves else 's'}{edge[1]})",
#                 edge_group
#             )
#         )
#     )

#     with open(filepath, '+a') as file:
#         for line in file:
#             if line == "# =========== Place to generated topology class ===========\n":
#                 break
#         file.write(sw_ext_intf_s)
#         file.write(f'''

# {sw_ext_intf_s}

# class MyTopology(Topo):
#     "Auto generated topology for this Mininet Node"

#     def __init__(self):
#         super().__init__()
#         "Add hosts and swiches"
#         {nodes_s}
        
#         "Add links"
#         {links_s}

# '''
#         )

#         for line in file:
#             if line == "# ============= Place to Intf interface name ==============":
#                 break
#         file.write(
#             f"        intfName = '{BASE_INTF_INTERFACE}'\n"
#         )



    

if __name__ == '__main__':
    a = NPS()
    a.start()
