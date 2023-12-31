from typing import Dict, Any, List, Union, TextIO

from config import HOST_NETMASK, LINK_DELAY, NO_DELAY_FLAG


def gen_mn_ns_script_by_template(
        file,
        nodes_ext_intf,
        node_group,
        edge_group,
        ext_intf_list,
        leaves,
        node_ctrl_map,
        hosts_net_services,
):
    """Generate turn on script for Cluster node with network services.

    Args:
        file: File discriptor of future turn on script.
        nodes_ext_intf: Cluster node external network interface name.
        node_group: Group ID to node-list map.
        edge_group: Group ID to edge-list map.
        ext_intf_list: External network interface name to the node group.
        leaves: List of leave-node in network graph.
    """
    file.write("#!/usr/bin/env python\n")
    file.write("\n")
    file.write("\n")
    file.write("from optparse import OptionParser\n")
    file.write("import os\n")
    file.write("import sys\n")
    file.write("import time\n")
    file.write("import re\n")
    file.write("\n")
    file.write("# Fix setuptools' evil madness, and open up (more?) security holes\n")
    file.write("if 'PYTHONPATH' in os.environ:\n")
    file.write("    sys.path = os.environ[ 'PYTHONPATH' ].split( ':' ) + sys.path\n")
    file.write("\n")
    file.write("from mininet.clean import cleanup\n")
    file.write("from mininet.cli import CLI\n")
    file.write("from mininet.log import lg, LEVELS, info\n")
    file.write("from mininet.net import Mininet, MininetWithControlNet, VERSION\n")
    file.write(
        "from mininet.node import ( Host, CPULimitedHost, Controller, OVSController,\n"
    )
    file.write(
        "                           NOX, RemoteController, UserSwitch, OVSKernelSwitch),\n"
    )
    file.write("from mininet.link import Link, TCLink, Intf\n")
    file.write(
        "from mininet.topo import Topo, SingleSwitchTopo, LinearTopo, SingleSwitchReversedTopo\n"
    )
    file.write("from mininet.topolib import TreeTopo\n")
    file.write("from mininet.util import custom, quietRun\n")
    file.write("from mininet.util import buildTopo\n")
    file.write("\n")
    file.write("\n")
    file.write("sw_ext_intf = [")
    for i, node in enumerate(ext_intf_list):
        file.write("'s")
        file.write(str(node))
        file.write("'")
        if i != len(ext_intf_list) - 1:
            file.write(",")
    file.write("]")
    file.write("\n")
    file.write("\n")
    file.write("class MyTopo( Topo ):\n")
    file.write('    "Auto generated topology for this Mininet Node"\n')
    file.write("    def __init__( self ):\n")
    file.write("        Topo.__init__( self )\n")
    file.write("\n")
    file.write('        "Add hosts and swiches"\n')
    for node in node_group:
        if node in leaves:
            file.write("        h")
            file.write(str(node))
            file.write(" = self.addHost( 'h")
            file.write(str(node))
            file.write("' )\n")
        else:
            file.write("        s")
            file.write(str(node))
            file.write(" = self.addSwitch( 's")
            file.write(str(node))
            file.write("' )\n")
    file.write("\n")
    file.write('        "Add links"\n')
    for edge in edge_group:
        file.write("        self.addLink( ")
        if edge[0] in leaves:
            file.write("h")
        else:
            file.write("s")
        file.write(str(edge[0]))
        file.write(", ")
        if edge[1] in leaves:
            file.write("h")
        else:
            file.write("s")
        file.write(str(edge[1]))
        file.write(" )\n")
    file.write("\n")
    file.write("\n")
    file.write("def checkIntf( intf ):\n")
    file.write('    "Make sure intf exists and is not configured."\n')
    file.write("    if ( ' %s:' % intf ) not in quietRun( 'ip link show' ):\n")
    file.write("        error( 'Error:', intf, 'does not exist!\\n' )\n")
    file.write("        exit( 1 )\n")
    file.write(
        "    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', quietRun( 'ifconfig ' + intf ) )\n"
    )
    file.write("    if ips:\n")
    file.write("        error( 'Error:', intf, 'has an IP address,'\n")
    file.write("                               'and is probably in use!\\n' )\n")
    file.write("        exit( 1 )\n")
    file.write("\n")
    file.write("#navy\n")
    file.write("import mininet.services\n")
    file.write("\n")
    file.write("# built in topologies, created only when run\n")
    file.write("TOPODEF = 'minimal'\n")
    file.write("TOPOS = { 'minimal': lambda: SingleSwitchTopo( k=2 ),\n")
    file.write("          'linear': LinearTopo,\n")
    file.write("          'reversed': SingleSwitchReversedTopo,\n")
    file.write("          'single': SingleSwitchTopo,\n")
    file.write("          'tree': TreeTopo }\n")
    file.write("\n")
    file.write("SWITCHDEF = 'ovsk'\n")
    file.write("SWITCHES = { 'user': UserSwitch,\n")
    file.write("             'ovsk': OVSKernelSwitch}\n")
    file.write("\n")
    file.write("HOSTDEF = 'proc'\n")
    file.write("HOSTS = { 'proc': Host,\n")
    file.write("          'rt': custom( CPULimitedHost, sched='rt' ),\n")
    file.write("          'cfs': custom( CPULimitedHost, sched='cfs' ) }\n")
    file.write("\n")
    file.write("CONTROLLERDEF = 'ovsc'\n")
    file.write("CONTROLLERS = { 'ref': Controller,\n")
    file.write("                'ovsc': OVSController,\n")
    file.write("                'nox': NOX,\n")
    file.write("                'remote': RemoteController,\n")
    file.write("               'none': lambda name: None }\n")
    file.write("\n")
    file.write("LINKDEF = 'default'\n")
    file.write("LINKS = { 'default': Link,\n")
    file.write("          'tc': TCLink }\n")
    file.write("\n")
    file.write("\n")
    file.write("# optional tests to run\n")
    file.write(
        "TESTS = [ 'cli', 'build', 'pingall', 'pingpair', 'iperf', 'all', 'iperfudp',\n"
    )
    file.write("            'none' ]\n")
    file.write("\n")
    file.write("ALTSPELLING = { 'pingall': 'pingAll',\n")
    file.write("                'pingpair': 'pingPair',\n")
    file.write("                'iperfudp': 'iperfUdp',\n")
    file.write("                'iperfUDP': 'iperfUdp' }\n")
    file.write("\n")
    file.write("\n")
    file.write("def addDictOption( opts, choicesDict, default, name, helpStr=None ):\n")
    file.write('    """Convenience function to add choices dicts to OptionParser.\n')
    file.write("       opts: OptionParser instance\n")
    file.write(
        "       choicesDict: dictionary of valid choices, must include default\n"
    )
    file.write("       default: default choice key\n")
    file.write("       name: long option name\n")
    file.write('       help: string"""\n')
    file.write("    if default not in choicesDict:\n")
    file.write(
        "        raise Exception( 'Invalid  default %s for choices dict: %s' %\n"
    )
    file.write("                         ( default, name ) )\n")
    file.write("    if not helpStr:\n")
    file.write("        helpStr = ( '|'.join( sorted( choicesDict.keys() ) ) +\n")
    file.write("                    '[,param=value...]' )\n")
    file.write("    opts.add_option( '--' + name,\n")
    file.write("                     type='string',\n")
    file.write("                     default = default,\n")
    file.write("                     help = helpStr )\n")
    file.write("\n")
    file.write("\n")
    file.write("def version( *_args ):\n")
    file.write('    "Print Mininet version and exit"\n')
    file.write('    print(VERSION)\n')
    file.write("    exit()\n")
    file.write("\n")
    file.write("class MininetRunner( object ):\n")
    file.write('    "Build, setup, and run Mininet."\n')
    file.write("\n")
    file.write("    def __init__( self ):\n")
    file.write('        "Init."\n')
    file.write("        self.options = None\n")
    file.write("        self.args = None  # May be used someday for more CLI scripts\n")
    file.write("        self.validate = None\n")
    file.write("\n")
    file.write("        self.parseArgs()\n")
    file.write("        self.setup()\n")
    file.write("        self.begin()\n")
    file.write("\n")
    file.write("    def setCustom( self, name, value ):\n")
    file.write('        "Set custom parameters for MininetRunner."\n')
    file.write("        if name in ( 'topos', 'switches', 'hosts', 'controllers' ):\n")
    file.write("            # Update dictionaries\n")
    file.write("            param = name.upper()\n")
    file.write("            globals()[ param ].update( value )\n")
    file.write("        elif name == 'validate':\n")
    file.write("            # Add custom validate function\n")
    file.write("            self.validate = value\n")
    file.write("        else:\n")
    file.write("            # Add or modify global variable or class\n")
    file.write("            globals()[ name ] = value\n")
    file.write("\n")
    file.write("    def parseCustomFile( self, fileName ):\n")
    file.write(
        '        "Parse custom file and add params before parsing cmd-line options."\n'
    )
    file.write("        customs = {}\n")
    file.write("        if os.path.isfile( fileName ):\n")
    file.write("            execfile( fileName, customs, customs )\n")
    file.write("            for name, val in customs.iteritems():\n")
    file.write("                self.setCustom( name, val )\n")
    file.write("        else:\n")
    file.write(
        "            raise Exception( 'could not find custom file: %s' % fileName )\n"
    )
    file.write("\n")
    file.write("    def parseArgs( self ):\n")
    file.write('        """Parse command-line args and return options object.\n')
    file.write('           returns: opts parse options dict"""\n')
    file.write("        if '--custom' in sys.argv:\n")
    file.write("            index = sys.argv.index( '--custom' )\n")
    file.write("            if len( sys.argv ) > index + 1:\n")
    file.write("                filename = sys.argv[ index + 1 ]\n")
    file.write("                self.parseCustomFile( filename )\n")
    file.write("            else:\n")
    file.write("                raise Exception( 'Custom file name not found' )\n")
    file.write("\n")
    file.write(
        '        desc = ( "The %prog utility creates Mininet network from the\\n"\n'
    )
    file.write(
        '                 "command line. It can create parametrized topologies,\\n"\n'
    )
    file.write('                 "invoke the Mininet CLI, and run tests." )\n')
    file.write("\n")
    file.write("        usage = ( '%prog [options]\\n'\n")
    file.write("                  '(type %prog -h for details)' )\n")
    file.write("\n")
    file.write("        opts = OptionParser( description=desc, usage=usage )\n")
    file.write("        addDictOption( opts, SWITCHES, SWITCHDEF, 'switch' )\n")
    file.write("        addDictOption( opts, HOSTS, HOSTDEF, 'host' )\n")
    file.write(
        "        addDictOption( opts, CONTROLLERS, CONTROLLERDEF, 'controller' )\n"
    )
    file.write("        addDictOption( opts, LINKS, LINKDEF, 'link' )\n")
    file.write("        addDictOption( opts, TOPOS, TOPODEF, 'topo' )\n")
    file.write("\n")
    file.write("        opts.add_option( '--clean', '-c', action='store_true',\n")
    file.write("                         default=False, help='clean and exit' )\n")
    file.write("        opts.add_option( '--custom', type='string', default=None,\n")
    file.write(
        "                         help='read custom topo and node params from .py' +\n"
    )
    file.write("                         'file' )\n")
    file.write("        opts.add_option( '--test', type='choice', choices=TESTS,\n")
    file.write("                         default=TESTS[ 0 ],\n")
    file.write("                         help='|'.join( TESTS ) )\n")
    file.write("        opts.add_option( '--xterms', '-x', action='store_true',\n")
    file.write(
        "                         default=False, help='spawn xterms for each node' )\n"
    )
    file.write(
        "        opts.add_option( '--ipbase', '-i', type='string', default='10.0.0.0/8',\n"
    )
    file.write("                         help='base IP address for hosts' )\n")
    file.write("        opts.add_option( '--mac', action='store_true',\n")
    file.write(
        "                         default=False, help='automatically set host MACs' )\n"
    )
    file.write("        opts.add_option( '--arp', action='store_true',\n")
    file.write(
        "                         default=False, help='set all-pairs ARP entries' )\n"
    )
    file.write("        opts.add_option( '--verbosity', '-v', type='choice',\n")
    file.write("                         choices=LEVELS.keys(), default = 'info',\n")
    file.write("                         help = '|'.join( LEVELS.keys() )  )\n")
    file.write("        opts.add_option( '--innamespace', action='store_true',\n")
    file.write(
        "                         default=False, help='sw and ctrl in namespace?' )\n"
    )
    file.write("        opts.add_option( '--listenport', type='int', default=6634,\n")
    file.write(
        "                         help='base port for passive switch listening' )\n"
    )
    file.write("        opts.add_option( '--nolistenport', action='store_true',\n")
    file.write(
        '                         default=False, help="don\'t use passive listening " +\n'
    )
    file.write('                         "port")\n')
    file.write("        opts.add_option( '--pre', type='string', default=None,\n")
    file.write("                         help='CLI script to run before tests' )\n")
    file.write("        opts.add_option( '--post', type='string', default=None,\n")
    file.write("                         help='CLI script to run after tests' )\n")
    file.write("        opts.add_option( '--pin', action='store_true',\n")
    file.write(
        '                         default=False, help="pin hosts to CPU cores "\n'
    )
    file.write('                         "(requires --host cfs or --host rt)" )\n')
    file.write(
        "        opts.add_option( '--version', action='callback', callback=version )\n"
    )
    file.write("\n")
    file.write("        self.options, self.args = opts.parse_args()\n")
    file.write("\n")
    file.write("    def setup( self ):\n")
    file.write('        "Setup and validate environment."\n')
    file.write("\n")
    file.write("        # set logging verbosity\n")
    file.write("        if LEVELS[self.options.verbosity] > LEVELS['output']:\n")
    file.write(
        "            print ( '*** WARNING: selected verbosity level (%s) will hide CLI '\n"
    )
    file.write("                    'output!\\n'\n")
    file.write(
        "                    'Please restart Mininet with -v [debug, info, output].'\n"
    )
    file.write("                    % self.options.verbosity )\n")
    file.write("        lg.setLogLevel( self.options.verbosity )\n")
    file.write("\n")
    file.write("    def begin( self ):\n")
    file.write('        "Create and run mininet."\n')
    file.write("\n")
    file.write("        if self.options.clean:\n")
    file.write("            cleanup()\n")
    file.write("            exit()\n")
    file.write("\n")
    file.write("        start = time.time()\n")
    file.write("\n")
    file.write("#navy\n")
    file.write("        #topo = buildTopo( TOPOS, self.options.topo )\n")
    file.write("        topo = MyTopo()\n")
    file.write("        switch = addSwitch(self.options.switch )\n")
    file.write("        host = addHost(self.options.host )\n")
    file.write("        controller = lambda name: RemoteController( name,ip='")
    file.write(node_ctrl_map[0])
    file.write("',port=int('")
    file.write(node_ctrl_map[1])
    file.write("') )\n")
    file.write("        link = addLink(self.options.link )\n")
    file.write("\n")
    file.write("        if self.validate:\n")
    file.write("            self.validate( self.options )\n")
    file.write("\n")
    file.write("        inNamespace = self.options.innamespace\n")
    file.write("        #navy\n")
    file.write("        #Net = MininetWithControlNet if inNamespace else Mininet\n")
    file.write("        Net = mininet.services.wrpMininet\n")
    file.write("\n")
    file.write("        ipBase = self.options.ipbase\n")
    file.write("        xterms = self.options.xterms\n")
    file.write("        mac = self.options.mac\n")
    file.write("        arp = self.options.arp\n")
    file.write("        pin = self.options.pin\n")
    file.write("        listenPort = None\n")
    file.write("        if not self.options.nolistenport:\n")
    file.write("            listenPort = self.options.listenport\n")
    file.write("\n")
    file.write("\n")
    file.write("        intfName = '")
    file.write(nodes_ext_intf)
    file.write("'\n")
    file.write("        info( '*** Checking', intfName, '\\n' )\n")
    file.write("        checkIntf( intfName )\n")
    file.write("\n")
    file.write("        mn = Net( topo=topo,\n")
    file.write("            switch=switch, host=host, controller=controller,\n")
    file.write("            link=link,\n")
    file.write("            ipBase=ipBase,\n")
    file.write("            inNamespace=inNamespace,\n")
    file.write("            xterms=xterms, autoSetMacs=mac,\n")
    file.write("            autoStaticArp=arp, autoPinCpus=pin,\n")
    file.write("#navy\n")
    file.write("#           listenPort=listenPort )\n")
    file.write("            listenPort=listenPort, services = True )\n")
    file.write("\n")
    file.write("\n")
    file.write("        for sw in mn.switches:\n")
    file.write("            if sw.name in sw_ext_intf:\n")
    file.write(
        "                info( '*** Adding hardware interface', intfName, 'to switch',\n"
    )
    file.write("                    sw.name, '\\n' )\n")
    file.write("                _intf = Intf( intfName, node=sw )\n")
    file.write("\n")
    file.write(
        "        info( '*** Note: you may need to reconfigure the interfaces for '\n"
    )
    file.write("            'the Mininet hosts:\\n', mn.hosts, '\\n' )\n")
    file.write("\n")
    file.write("#navy\n")
    file.write("#Add services here\n")
    for host in hosts_net_services.keys():
        if (int(host) in leaves) and (int(host) in node_group):
            for net_service, status in hosts_net_services[host].items():
                if status == True:
                    if net_service == "dhcp":
                        file.write(
                            "        mn.add_preconf_service( 'h"
                            + host
                            + "', 2 , '"
                            + net_service
                            + "' )\n"
                        )
                    elif net_service == "dhcpd":
                        file.write(
                            "        mn.add_preconf_service( 'h"
                            + host
                            + "', 1 , '"
                            + net_service
                            + "' )\n"
                        )
                    else:
                        file.write(
                            "        mn.add_preconf_service( 'h"
                            + host
                            + "', 3 , '"
                            + net_service
                            + "' )\n"
                        )
    file.write("#-----------------\n")
    file.write("\n")
    file.write("\n")
    file.write("        if self.options.pre:\n")
    file.write("            CLI( mn, script=self.options.pre )\n")
    file.write("\n")
    file.write("        test = self.options.test\n")
    file.write("        test = ALTSPELLING.get( test, test )\n")
    file.write("\n")
    file.write("        mn.start()\n")
    file.write("\n")
    file.write("        if test == 'none':\n")
    file.write("            pass\n")
    file.write("        elif test == 'all':\n")
    file.write("            mn.start()\n")
    file.write("            mn.ping()\n")
    file.write("            mn.iperf()\n")
    file.write("        elif test == 'cli':\n")
    file.write("            CLI( mn )\n")
    file.write("        elif test != 'build':\n")
    file.write("            getattr( mn, test )()\n")
    file.write("\n")
    file.write("        if self.options.post:\n")
    file.write("            CLI( mn, script=self.options.post )\n")
    file.write("\n")
    file.write("        mn.stop()\n")
    file.write("\n")
    file.write("        elapsed = float( time.time() - start )\n")
    file.write("        info( 'completed in %0.3f seconds\\n' % elapsed )\n")
    file.write("\n")
    file.write("\n")
    file.write('if __name__ == "__main__":\n')
    file.write("    MininetRunner()\n")


def gen_mn_ns_script_by_template_with_custom_host_ip(
        file: TextIO,
        node: Dict[str, str],
        group: Dict[str, List[Union[str, int]]],
        spec_group: Dict[str, List[Union[str, int]]],
        leaves: List[int],
        hosts_net_services: Any,
        hosts: Dict[str, Dict[str, str]],
) -> None:
    """
    Generate turn on script for Cluster node with network services and with custom host IP addresses

    :param file: File descriptor of future turn on script.
    :type file: io.TextIOWrapper
    :param node:
    :type node:
    :param group: Cluster node external network interface name.
    :type group: Dict[str, str]
    :param spec_group: Group ID to edge-list map.
    :type spec_group: Dict[str, List[Union[str, int]]]
    :param leaves: List of leave-node in network graph.
    :type leaves: List[int]
    :param hosts_net_services:
    :type hosts_net_services: Any
    :param hosts:
    :type hosts: Dict[str, str]
    """

    file.write("#!/usr/bin/env python\n")
    file.write("\n")
    file.write("\n")
    file.write("from optparse import OptionParser\n")
    file.write("import os\n")
    file.write("import sys\n")
    file.write("import time\n")
    file.write("import re\n")
    file.write("\n")
    file.write("# Fix setuptools' evil madness, and open up (more?) security holes\n")
    file.write("if 'PYTHONPATH' in os.environ:\n")
    file.write("    sys.path = os.environ[ 'PYTHONPATH' ].split( ':' ) + sys.path\n")
    file.write("\n")
    file.write("from mininet.clean import cleanup\n")
    file.write("from mininet.cli import CLI\n")
    file.write("from mininet.log import lg, LEVELS, info\n")
    file.write("from mininet.net import Mininet, MininetWithControlNet, VERSION\n")
    file.write(
        "from mininet.node import ( Host, CPULimitedHost, Controller, OVSController,\n"
    )
    file.write(
        "                           NOX, RemoteController, UserSwitch, OVSKernelSwitch)\n"
    )
    file.write("from mininet.link import Link, TCLink, Intf\n")
    file.write(
        "from mininet.topo import Topo, SingleSwitchTopo, LinearTopo, SingleSwitchReversedTopo\n"
    )
    file.write("from mininet.topolib import TreeTopo\n")
    file.write("from mininet.util import custom, quietRun\n")
    file.write("from mininet.util import buildTopo\n")
    file.write("\n")
    file.write("\n")
    file.write("sw_ext_intf = [")
    for i, vertex in enumerate(spec_group["vertexes"]):
        file.write("'s")
        file.write(str(vertex))
        file.write("'")
        if i != len(spec_group["vertexes"]) - 1:
            file.write(",")
    file.write("]")
    file.write("\n")
    file.write("\n")
    file.write("class MyTopo( Topo ):\n")
    file.write('    "Auto generated topology for this Mininet Node"\n')
    file.write("    def __init__( self ):\n")
    file.write("        Topo.__init__( self )\n")
    file.write("\n")
    file.write('        "Add hosts and swiches"\n')
    # Define IPs
    for vertex in group["vertexes"]:
        if vertex in leaves:
            file.write("        h")
            file.write(str(vertex))
            file.write(" = self.addHost( 'h")
            file.write(str(vertex))
            file.write("', ip='")
            file.write(hosts["h" + str(vertex)]["IP"])
            file.write("/")
            file.write(str(HOST_NETMASK))
            file.write("' )\n")
            # curr_host_ip = get_next_IP(curr_host_ip)
        else:
            file.write("        s")
            file.write(str(vertex))
            file.write(" = self.addSwitch( 's")
            file.write(str(vertex))
            file.write("' )\n")
    file.write("\n")
    file.write('        "Add links"\n')
    for edge_in_gr in group["edges"]:
        file.write("        self.addLink( ")
        if edge_in_gr[0] in leaves:
            file.write("h")
        else:
            file.write("s")
        file.write(str(edge_in_gr[0]))
        file.write(", ")
        if edge_in_gr[1] in leaves:
            file.write("h")
        else:
            file.write("s")
        file.write(str(edge_in_gr[1]))
        if NO_DELAY_FLAG:
            file.write(")\n")
        else:
            file.write(", delay='")
            file.write(str(LINK_DELAY))
            file.write("ms')\n")
    file.write("\n")
    file.write("\n")
    file.write("def checkIntf( intf ):\n")
    file.write('    "Make sure intf exists and is not configured."\n')
    file.write("    if ( ' %s:' % intf ) not in quietRun( 'ip link show' ):\n")
    file.write("        error( 'Error:', intf, 'does not exist!\\n' )\n")
    file.write("        exit( 1 )\n")
    file.write(
        "    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', quietRun( 'ifconfig ' + intf ) )\n"
    )
    file.write("    if ips:\n")
    file.write("        error( 'Error:', intf, 'has an IP address,'\n")
    file.write("                               'and is probably in use!\\n' )\n")
    file.write("        exit( 1 )\n")
    file.write("\n")
    file.write("#navy\n")
    file.write("import mininet.services\n")
    file.write("\n")
    file.write("# built in topologies, created only when run\n")
    file.write("TOPODEF = 'minimal'\n")
    file.write("TOPOS = { 'minimal': lambda: SingleSwitchTopo( k=2 ),\n")
    file.write("          'linear': LinearTopo,\n")
    file.write("          'reversed': SingleSwitchReversedTopo,\n")
    file.write("          'single': SingleSwitchTopo,\n")
    file.write("          'tree': TreeTopo }\n")
    file.write("\n")
    file.write("SWITCHDEF = 'ovsk'\n")
    file.write("SWITCHES = { 'user': UserSwitch,\n")
    file.write("             'ovsk': OVSKernelSwitch}\n")
    file.write("\n")
    file.write("HOSTDEF = 'proc'\n")
    file.write("HOSTS = { 'proc': Host,\n")
    file.write("          'rt': custom( CPULimitedHost, sched='rt' ),\n")
    file.write("          'cfs': custom( CPULimitedHost, sched='cfs' ) }\n")
    file.write("\n")
    file.write("CONTROLLERDEF = 'ovsc'\n")
    file.write("CONTROLLERS = { 'ref': Controller,\n")
    file.write("                'ovsc': OVSController,\n")
    file.write("                'nox': NOX,\n")
    file.write("                'remote': RemoteController,\n")
    file.write("               'none': lambda name: None }\n")
    file.write("\n")
    file.write("LINKDEF = 'default'\n")
    file.write("LINKS = { 'default': TCLink,\n")
    file.write("          'tc': TCLink }\n")
    file.write("\n")
    file.write("\n")
    file.write("# optional tests to run\n")
    file.write(
        "TESTS = [ 'cli', 'build', 'pingall', 'pingpair', 'iperf', 'all', 'iperfudp',\n"
    )
    file.write("            'none' ]\n")
    file.write("\n")
    file.write("ALTSPELLING = { 'pingall': 'pingAll',\n")
    file.write("                'pingpair': 'pingPair',\n")
    file.write("                'iperfudp': 'iperfUdp',\n")
    file.write("                'iperfUDP': 'iperfUdp' }\n")
    file.write("\n")
    file.write("\n")
    file.write("def addDictOption( opts, choicesDict, default, name, helpStr=None ):\n")
    file.write('    """Convenience function to add choices dicts to OptionParser.\n')
    file.write("       opts: OptionParser instance\n")
    file.write(
        "       choicesDict: dictionary of valid choices, must include default\n"
    )
    file.write("       default: default choice key\n")
    file.write("       name: long option name\n")
    file.write('       help: string"""\n')
    file.write("    if default not in choicesDict:\n")
    file.write(
        "        raise Exception( 'Invalid  default %s for choices dict: %s' %\n"
    )
    file.write("                         ( default, name ) )\n")
    file.write("    if not helpStr:\n")
    file.write("        helpStr = ( '|'.join( sorted( choicesDict.keys() ) ) +\n")
    file.write("                    '[,param=value...]' )\n")
    file.write("    opts.add_option( '--' + name,\n")
    file.write("                     type='string',\n")
    file.write("                     default = default,\n")
    file.write("                     help = helpStr )\n")
    file.write("\n")
    file.write("\n")
    file.write("def version( *_args ):\n")
    file.write('    "Print Mininet version and exit"\n')
    file.write('    print("%s" % VERSION)\n')
    file.write("    exit()\n")
    file.write("\n")
    file.write("class MininetRunner( object ):\n")
    file.write('    "Build, setup, and run Mininet."\n')
    file.write("\n")
    file.write("    def __init__( self ):\n")
    file.write('        "Init."\n')
    file.write("        self.options = None\n")
    file.write("        self.args = None  # May be used someday for more CLI scripts\n")
    file.write("        self.validate = None\n")
    file.write("\n")
    file.write("        self.parseArgs()\n")
    file.write("        self.setup()\n")
    file.write("        self.begin()\n")
    file.write("\n")
    file.write("    def setCustom( self, name, value ):\n")
    file.write('        "Set custom parameters for MininetRunner."\n')
    file.write("        if name in ( 'topos', 'switches', 'hosts', 'controllers' ):\n")
    file.write("            # Update dictionaries\n")
    file.write("            param = name.upper()\n")
    file.write("            globals()[ param ].update( value )\n")
    file.write("        elif name == 'validate':\n")
    file.write("            # Add custom validate function\n")
    file.write("            self.validate = value\n")
    file.write("        else:\n")
    file.write("            # Add or modify global variable or class\n")
    file.write("            globals()[ name ] = value\n")
    file.write("\n")
    file.write("    def parseCustomFile( self, fileName ):\n")
    file.write(
        '        "Parse custom file and add params before parsing cmd-line options."\n'
    )
    file.write("        customs = {}\n")
    file.write("        if os.path.isfile( fileName ):\n")
    file.write("            execfile( fileName, customs, customs )\n")
    file.write("            for name, val in customs.iteritems():\n")
    file.write("                self.setCustom( name, val )\n")
    file.write("        else:\n")
    file.write(
        "            raise Exception( 'could not find custom file: %s' % fileName )\n"
    )
    file.write("\n")
    file.write("    def parseArgs( self ):\n")
    file.write('        """Parse command-line args and return options object.\n')
    file.write('           returns: opts parse options dict"""\n')
    file.write("        if '--custom' in sys.argv:\n")
    file.write("            index = sys.argv.index( '--custom' )\n")
    file.write("            if len( sys.argv ) > index + 1:\n")
    file.write("                filename = sys.argv[ index + 1 ]\n")
    file.write("                self.parseCustomFile( filename )\n")
    file.write("            else:\n")
    file.write("                raise Exception( 'Custom file name not found' )\n")
    file.write("\n")
    file.write(
        '        desc = ( "The %prog utility creates Mininet network from the\\n"\n'
    )
    file.write(
        '                 "command line. It can create parametrized topologies,\\n"\n'
    )
    file.write('                 "invoke the Mininet CLI, and run tests." )\n')
    file.write("\n")
    file.write("        usage = ( '%prog [options]\\n'\n")
    file.write("                  '(type %prog -h for details)' )\n")
    file.write("\n")
    file.write("        opts = OptionParser( description=desc, usage=usage )\n")
    file.write("        addDictOption( opts, SWITCHES, SWITCHDEF, 'switch' )\n")
    file.write("        addDictOption( opts, HOSTS, HOSTDEF, 'host' )\n")
    file.write(
        "        addDictOption( opts, CONTROLLERS, CONTROLLERDEF, 'controller' )\n"
    )
    file.write("        addDictOption( opts, LINKS, LINKDEF, 'link' )\n")
    file.write("        addDictOption( opts, TOPOS, TOPODEF, 'topo' )\n")
    file.write("\n")
    file.write("        opts.add_option( '--clean', '-c', action='store_true',\n")
    file.write("                         default=False, help='clean and exit' )\n")
    file.write("        opts.add_option( '--custom', type='string', default=None,\n")
    file.write(
        "                         help='read custom topo and node params from .py' +\n"
    )
    file.write("                         'file' )\n")
    file.write("        opts.add_option( '--test', type='choice', choices=TESTS,\n")
    file.write("                         default=TESTS[ 0 ],\n")
    file.write("                         help='|'.join( TESTS ) )\n")
    file.write("        opts.add_option( '--xterms', '-x', action='store_true',\n")
    file.write(
        "                         default=False, help='spawn xterms for each node' )\n"
    )
    file.write(
        "        opts.add_option( '--ipbase', '-i', type='string', default='10.0.0.0/8',\n"
    )
    file.write("                         help='base IP address for hosts' )\n")
    file.write("        opts.add_option( '--mac', action='store_true',\n")
    file.write(
        "                         default=False, help='automatically set host MACs' )\n"
    )
    file.write("        opts.add_option( '--arp', action='store_true',\n")
    file.write(
        "                         default=False, help='set all-pairs ARP entries' )\n"
    )
    file.write("        opts.add_option( '--verbosity', '-v', type='choice',\n")
    file.write("                         choices=LEVELS.keys(), default = 'info',\n")
    file.write("                         help = '|'.join( LEVELS.keys() )  )\n")
    file.write("        opts.add_option( '--innamespace', action='store_true',\n")
    file.write(
        "                         default=False, help='sw and ctrl in namespace?' )\n"
    )
    file.write("        opts.add_option( '--listenport', type='int', default=6634,\n")
    file.write(
        "                         help='base port for passive switch listening' )\n"
    )
    file.write("        opts.add_option( '--nolistenport', action='store_true',\n")
    file.write(
        '                         default=False, help="don\'t use passive listening " +\n'
    )
    file.write('                         "port")\n')
    file.write("        opts.add_option( '--pre', type='string', default=None,\n")
    file.write("                         help='CLI script to run before tests' )\n")
    file.write("        opts.add_option( '--post', type='string', default=None,\n")
    file.write("                         help='CLI script to run after tests' )\n")
    file.write("        opts.add_option( '--pin', action='store_true',\n")
    file.write(
        '                         default=False, help="pin hosts to CPU cores "\n'
    )
    file.write('                         "(requires --host cfs or --host rt)" )\n')
    file.write(
        "        opts.add_option( '--version', action='callback', callback=version )\n"
    )
    file.write("\n")
    file.write("        self.options, self.args = opts.parse_args()\n")
    file.write("\n")
    file.write("    def setup( self ):\n")
    file.write('        "Setup and validate environment."\n')
    file.write("\n")
    file.write("        # set logging verbosity\n")
    file.write("        if LEVELS[self.options.verbosity] > LEVELS['output']:\n")
    file.write(
        "            print ( '*** WARNING: selected verbosity level (%s) will hide CLI '\n"
    )
    file.write("                    'output!\\n'\n")
    file.write(
        "                    'Please restart Mininet with -v [debug, info, output].'\n"
    )
    file.write("                    % self.options.verbosity )\n")
    file.write("        lg.setLogLevel( self.options.verbosity )\n")
    file.write("\n")
    file.write("    def begin( self ):\n")
    file.write('        "Create and run mininet."\n')
    file.write("\n")
    file.write("        if self.options.clean:\n")
    file.write("            cleanup()\n")
    file.write("            exit()\n")
    file.write("\n")
    file.write("        start = time.time()\n")
    file.write("\n")
    file.write("#navy\n")
    file.write("        #topo = buildTopo( TOPOS, self.options.topo )\n")
    file.write("        topo = MyTopo()\n")
    file.write("        switch = addSwitch(self.options.switch )\n")
    file.write("        host = addHost(self.options.host )\n")
    file.write("        controller = lambda name: RemoteController( name,ip='")
    file.write(node["controller"][0])
    file.write("',port=int('")
    file.write(node["controller"][1])
    file.write("') )\n")
    file.write("        link = addLink(self.options.link )\n")
    file.write("\n")
    file.write("        if self.validate:\n")
    file.write("            self.validate( self.options )\n")
    file.write("\n")
    file.write("        inNamespace = self.options.innamespace\n")
    file.write("        #navy\n")
    file.write("        #Net = MininetWithControlNet if inNamespace else Mininet\n")
    file.write("        Net = mininet.services.wrpMininet\n")
    file.write("\n")
    file.write("        ipBase = self.options.ipbase\n")
    file.write("        xterms = self.options.xterms\n")
    file.write("        mac = self.options.mac\n")
    file.write("        arp = self.options.arp\n")
    file.write("        pin = self.options.pin\n")
    file.write("        listenPort = None\n")
    file.write("        if not self.options.nolistenport:\n")
    file.write("            listenPort = self.options.listenport\n")
    file.write("\n")
    file.write("\n")
    file.write("        intfName = '")
    file.write(node["out_intf"])
    file.write("'\n")
    file.write("        info( '*** Checking', intfName, '\\n' )\n")
    file.write("        checkIntf( intfName )\n")
    file.write("\n")
    file.write("        mn = Net( topo=topo,\n")
    file.write("            switch=switch, host=host, controller=controller,\n")
    file.write("            link=link,\n")
    file.write("            ipBase=ipBase,\n")
    file.write("            inNamespace=inNamespace,\n")
    file.write("            xterms=xterms, autoSetMacs=mac,\n")
    file.write("            autoStaticArp=arp, autoPinCpus=pin,\n")
    file.write("#navy\n")
    file.write("#           listenPort=listenPort )\n")
    file.write("            listenPort=listenPort, services = True )\n")
    file.write("\n")
    file.write("\n")
    file.write("        for sw in mn.switches:\n")
    file.write("            if sw.name in sw_ext_intf:\n")
    file.write(
        "                info( '*** Adding hardware interface', intfName, 'to switch',\n"
    )
    file.write("                    sw.name, '\\n' )\n")
    file.write("                _intf = Intf( intfName, node=sw )\n")
    file.write("\n")
    file.write(
        "        info( '*** Note: you may need to reconfigure the interfaces for '\n"
    )
    file.write("            'the Mininet hosts:\\n', mn.hosts, '\\n' )\n")
    file.write("\n")
    file.write("#navy\n")
    file.write("#Add services here\n")
    for host in sorted(hosts_net_services.keys()):
        if (int(host) in leaves) and (int(host) in group["vertexes"]):
            for net_service, status in hosts_net_services[host].items():
                if status == True:
                    if net_service == "dhcp":
                        file.write(
                            "        mn.add_preconf_service( 'h"
                            + host
                            + "', 2 , '"
                            + net_service
                            + "' )\n"
                        )
                    elif net_service == "dhcpd":
                        file.write(
                            "        mn.add_preconf_service( 'h"
                            + host
                            + "', 1 , '"
                            + net_service
                            + "' )\n"
                        )
                    else:
                        file.write(
                            "        mn.add_preconf_service( 'h"
                            + host
                            + "', 3 , '"
                            + net_service
                            + "' )\n"
                        )
    file.write("#-----------------\n")
    file.write("\n")
    file.write("\n")
    file.write("        if self.options.pre:\n")
    file.write("            CLI( mn, script=self.options.pre )\n")
    file.write("\n")
    file.write("        test = self.options.test\n")
    file.write("        test = ALTSPELLING.get( test, test )\n")
    file.write("\n")
    file.write("        mn.start()\n")
    file.write("\n")
    file.write("        if test == 'none':\n")
    file.write("            pass\n")
    file.write("        elif test == 'all':\n")
    file.write("            mn.start()\n")
    file.write("            mn.ping()\n")
    file.write("            mn.iperf()\n")
    file.write("        elif test == 'cli':\n")
    file.write("            CLI( mn )\n")
    file.write("        elif test != 'build':\n")
    file.write("            getattr( mn, test )()\n")
    file.write("\n")
    file.write("        if self.options.post:\n")
    file.write("            CLI( mn, script=self.options.post )\n")
    file.write("\n")
    file.write("        mn.stop()\n")
    file.write("\n")
    file.write("        elapsed = float( time.time() - start )\n")
    file.write("        info( 'completed in %0.3f seconds\\n' % elapsed )\n")
    file.write("\n")
    file.write("\n")
    file.write('if __name__ == "__main__":\n')
    file.write("    MininetRunner()\n")


if __name__ == "__main__":
    file = open("test_sc", "w")
    nodes_ext_intf = "eth1"
    node_group = [0, 3, 4]
    edge_group = [(0, 3), (0, 4)]
    ext_intf_list = [0, 1, 2]
    leaves = [3, 4, 5, 6]
    node_ctrl_map = ("10.211.55.2", "6633")
    hosts_net_services = {
        "0": {
            "dhcp": False,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
        "1": {
            "dhcp": False,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
        "2": {
            "dhcp": False,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
        "3": {
            "dhcp": True,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
        "4": {
            "dhcp": False,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
        "5": {
            "dhcp": False,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
        "6": {
            "dhcp": False,
            "WEB": False,
            "VIDEO": False,
            "FTP": False,
            "P2P": False,
            "SMTP": False,
        },
    }

    gen_mn_ns_script_by_template(
        file,
        nodes_ext_intf,
        node_group,
        edge_group,
        ext_intf_list,
        leaves,
        node_ctrl_map,
        hosts_net_services,
    )
