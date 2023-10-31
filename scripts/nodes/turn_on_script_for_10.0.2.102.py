#!/usr/bin/env python 
import os 
import sys 
import time 
import re 
 
from functools import partial 
from optparse import OptionParser  # pylint: disable=deprecated-module 
from sys import exit  # pylint: disable=redefined-builtin 
 
# Fix setuptools' evil madness, and open up (more?) security holes 
if 'PYTHONPATH' in os.environ: 
    sys.path = os.environ[ 'PYTHONPATH' ].split( ':' ) + sys.path 
 
# pylint: disable=wrong-import-position 
 
from mininet.clean import cleanup 
import mininet.cli 
from mininet.log import lg, LEVELS, info, debug, warn, error, output 
from mininet.net import Mininet, MininetWithControlNet, VERSION 
from mininet.node import ( Host, CPULimitedHost, Controller, OVSController, 
                           Ryu, NOX, RemoteController, findController, 
                           DefaultController, NullController, 
                           UserSwitch, OVSSwitch, OVSBridge, 
                           IVSSwitch ) 
from mininet.nodelib import LinuxBridge 
from mininet.link import Link, TCLink, TCULink, OVSLink, Intf 
from mininet.topo import ( Topo, SingleSwitchTopo, LinearTopo, 
                           SingleSwitchReversedTopo, MinimalTopo ) 
from mininet.topolib import TreeTopo, TorusTopo 
from mininet.util import customClass, specialClass, splitArgs, buildTopo, quietRun 
 
# Experimental! cluster edition prototype 
from mininet.examples.cluster import ( MininetCluster, RemoteHost, 
                                       RemoteOVSSwitch, RemoteLink, 
                                       SwitchBinPlacer, RandomPlacer, 
                                       ClusterCleanup ) 
from mininet.examples.clustercli import ClusterCLI 
 
 
# ======================================================== 
 
sw_ext_intf = ['s0', 's12']
sw_ext_intf_edges = [('s0', 's12')] 
 
class MyTopology(Topo): 
    "Auto generated topology for this Mininet Node" 
 
    def __init__(self): 
        super().__init__() 
 
        "Add hosts and swiches" 
        s12 = self.addSwitch(name='s12', protocols='OpenFlow13', dpid='000000000000000D')
        h16 = self.addHost(name='h16', ip='1.2.3.7\16')
        h13 = self.addHost(name='h13', ip='1.2.3.8\16')
        h14 = self.addHost(name='h14', ip='1.2.3.9\16')
        "Add links"
        self.addLink(s12, h16, delay='5ms')
        self.addLink(s12, h13, delay='5ms')
        self.addLink(s12, h14, delay='5ms') 
# ======================================================== 
 
def checkIntf( intf ): 
    "Make sure intf exists and is not configured." 
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True ) 
    if not config: 
        error( 'Error:', intf, 'does not exist!\n' ) 
        exit( 1 ) 
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config ) 
    if ips: 
        error( 'Error:', intf, 'has an IP address,' 
               'and is probably in use!\n' ) 
        exit( 1 ) 
 
PLACEMENT = { 'block': SwitchBinPlacer, 'random': RandomPlacer } 
 
# built in topologies, created only when run 
TOPODEF = 'minimal' 
TOPOS = { 'minimal': MinimalTopo, 
          'linear': LinearTopo, 
          'reversed': SingleSwitchReversedTopo, 
          'single': SingleSwitchTopo, 
          'tree': TreeTopo, 
          'torus': TorusTopo } 
 
SWITCHDEF = 'default' 
SWITCHES = { 'user': UserSwitch, 
             'ovs': OVSSwitch, 
             'ovsbr' : OVSBridge, 
             # Keep ovsk for compatibility with 2.0 
             'ovsk': OVSSwitch, 
             'ivs': IVSSwitch, 
             'lxbr': LinuxBridge, 
             'default': OVSSwitch } 
 
HOSTDEF = 'proc' 
HOSTS = { 'proc': Host, 
          'rt': specialClass( CPULimitedHost, defaults=dict( sched='rt' ) ), 
          'cfs': specialClass( CPULimitedHost, defaults=dict( sched='cfs' ) ) } 
 
CONTROLLERDEF = 'default' 
CONTROLLERS = { 'ref': Controller, 
                'ovsc': OVSController, 
                'nox': NOX, 
                'remote': RemoteController, 
                'ryu': Ryu, 
                'default': DefaultController,  # Note: overridden below 
                'none': NullController } 
 
LINKDEF = 'default' 
LINKS = { 'default': Link,  # Note: overridden below 
          'tc': TCLink, 
          'tcu': TCULink, 
          'ovs': OVSLink } 
 
# TESTS dict can contain functions and/or Mininet() method names 
# XXX: it would be nice if we could specify a default test, but 
# this may be tricky 
TESTS = { name: True 
          for name in ( 'pingall', 'pingpair', 'iperf', 'iperfudp' ) } 
 
CLI = None  # Set below if needed 
 
# Locally defined tests 
def allTest( net ): 
    "Run ping and iperf tests" 
    net.start() 
    net.ping() 
    net.iperf() 
 
def nullTest( _net ): 
    "Null 'test' (does nothing)" 
    pass 
 
 
TESTS.update( all=allTest, none=nullTest, build=nullTest ) 
 
# Map to alternate spellings of Mininet() methods 
ALTSPELLING = { 'pingall': 'pingAll', 'pingpair': 'pingPair', 
                'iperfudp': 'iperfUdp' } 
 
def runTests( mn, options ): 
    """Run tests 
       mn: Mininet object 
       option: list of test optinos """ 
    # Split option into test name and parameters 
    for option in options: 
        # Multiple tests may be separated by '+' for now 
        for test in option.split( '+' ): 
            test, args, kwargs = splitArgs( test ) 
            test = ALTSPELLING.get( test.lower(), test ) 
            testfn = TESTS.get( test, test ) 
            if callable( testfn ): 
                testfn( mn, *args, **kwargs ) 
            elif hasattr( mn, test ): 
                getattr( mn, test )( *args, **kwargs ) 
            else: 
                raise Exception( 'Test %s is unknown - please specify one of ' 
                                 '%s ' % ( test, TESTS.keys() ) ) 
 
 
def addDictOption( opts, choicesDict, default, name, **kwargs ): 
    """Convenience function to add choices dicts to OptionParser. 
       opts: OptionParser instance 
       choicesDict: dictionary of valid choices, must include default 
       default: default choice key 
       name: long option name 
       kwargs: additional arguments to add_option""" 
    helpStr = ( '|'.join( sorted( choicesDict.keys() ) ) + 
                '[,param=value...]' ) 
    helpList = [ '%s=%s' % ( k, v.__name__ ) 
                 for k, v in choicesDict.items() ] 
    helpStr += ' ' + ( ' '.join( helpList ) ) 
    params = dict( type='string', default=default, help=helpStr ) 
    params.update( **kwargs ) 
    opts.add_option( '--' + name, **params ) 
 
def version( *_args ): 
    "Print Mininet version and exit" 
    output( "%s\n" % VERSION ) 
    exit() 
 
 
class MininetRunner( object ): 
    "Build, setup, and run Mininet." 
 
    def __init__( self ): 
        "Init." 
        self.options = None 
        self.args = None  # May be used someday for more CLI scripts 
        self.validate = None 
 
        self.parseArgs() 
        self.setup() 
        self.begin() 
 
    def custom( self, _option, _opt_str, value, _parser ): 
        """Parse custom file and add params. 
           option: option e.g. --custom 
           opt_str: option string e.g. --custom 
           value: the value the follows the option 
           parser: option parser instance""" 
        files = [] 
        if os.path.isfile( value ): 
            # Accept any single file (including those with commas) 
            files.append( value ) 
        else: 
            # Accept a comma-separated list of filenames 
            files += value.split(',') 
 
        for fileName in files: 
            customs = {} 
            if os.path.isfile( fileName ): 
                # pylint: disable=exec-used 
                with open( fileName ) as f: 
                    exec( compile( f.read(), fileName, 'exec' ), 
                          customs, customs ) 
                for name, val in customs.items(): 
                    self.setCustom( name, val ) 
            else: 
                raise Exception( 'could not find custom file: %s' % fileName ) 
 
    def setCustom( self, name, value ): 
        "Set custom parameters for MininetRunner." 
        if name in ( 'topos', 'switches', 'hosts', 'controllers', 'links' 
                     'testnames', 'tests' ): 
            # Update dictionaries 
            param = name.upper() 
            globals()[ param ].update( value ) 
        elif name == 'validate': 
            # Add custom validate function 
            self.validate = value 
        else: 
            # Add or modify global variable or class 
            globals()[ name ] = value 
 
    def setNat( self, _option, opt_str, value, parser ): 
        "Set NAT option(s)" 
        assert self  # satisfy pylint 
        parser.values.nat = True 
        # first arg, first char != '-' 
        if parser.rargs and parser.rargs[ 0 ][ 0 ] != '-': 
            value = parser.rargs.pop( 0 ) 
            _, args, kwargs = splitArgs( opt_str + ',' + value ) 
            parser.values.nat_args = args 
            parser.values.nat_kwargs = kwargs 
        else: 
            parser.values.nat_args = [] 
            parser.values.nat_kwargs = {} 
 
    def parseArgs( self ): 
        """Parse command-line args and return options object. 
           returns: opts parse options dict""" 
 
        desc = ( "The %prog utility creates Mininet network from the\n" 
                 "command line. It can create parametrized topologies,\n" 
                 "invoke the Mininet CLI, and run tests." ) 
 
        usage = ( '%prog [options]\n' 
                  '(type %prog -h for details)' ) 
 
        opts = OptionParser( description=desc, usage=usage ) 
        addDictOption( opts, SWITCHES, SWITCHDEF, 'switch' ) 
        addDictOption( opts, HOSTS, HOSTDEF, 'host' ) 
        addDictOption( opts, CONTROLLERS, [], 'controller', action='append' ) 
        addDictOption( opts, LINKS, LINKDEF, 'link' ) 
        addDictOption( opts, TOPOS, TOPODEF, 'topo' ) 
 
        opts.add_option( '--clean', '-c', action='store_true', 
                         default=False, help='clean and exit' ) 
        opts.add_option( '--custom', action='callback', 
                         callback=self.custom, 
                         type='string', 
                         help='read custom classes or params from .py file(s)' 
                         ) 
        opts.add_option( '--test', default=[], action='append', 
                         dest='test', help='|'.join( TESTS.keys() ) ) 
        opts.add_option( '--xterms', '-x', action='store_true', 
                         default=False, help='spawn xterms for each node' ) 
        opts.add_option( '--ipbase', '-i', type='string', default='10.0.0.0/8', 
                         help='base IP address for hosts' ) 
        opts.add_option( '--mac', action='store_true', 
                         default=False, help='automatically set host MACs' ) 
        opts.add_option( '--arp', action='store_true', 
                         default=False, help='set all-pairs ARP entries' ) 
        opts.add_option( '--verbosity', '-v', type='choice', 
                         choices=list( LEVELS.keys() ), default = 'info', 
                         help = '|'.join( LEVELS.keys() )  ) 
        opts.add_option( '--innamespace', action='store_true', 
                         default=False, help='sw and ctrl in namespace?' ) 
        opts.add_option( '--listenport', type='int', default=6654, 
                         help='base port for passive switch listening' ) 
        opts.add_option( '--nolistenport', action='store_true', 
                         default=False, help="don't use passive listening " + 
                         "port") 
        opts.add_option( '--pre', type='string', default=None, 
                         help='CLI script to run before tests' ) 
        opts.add_option( '--post', type='string', default=None, 
                         help='CLI script to run after tests' ) 
        opts.add_option( '--pin', action='store_true', 
                         default=False, help="pin hosts to CPU cores " 
                         "(requires --host cfs or --host rt)" ) 
        opts.add_option( '--nat', action='callback', callback=self.setNat, 
                         help="[option=val...] adds a NAT to the topology that" 
                         " connects Mininet hosts to the physical network." 
                         " Warning: This may route any traffic on the machine" 
                         " that uses Mininet's" 
                         " IP subnet into the Mininet network." 
                         " If you need to change" 
                         " Mininet's IP subnet, see the --ipbase option." ) 
        opts.add_option( '--version', action='callback', callback=version, 
                         help='prints the version and exits' ) 
        opts.add_option( '--wait', '-w', action='store_true', 
                         default=False, help='wait for switches to connect' ) 
        opts.add_option( '--twait', '-t', action='store', type='int', 
                         dest='wait', 
                         help='timed wait (s) for switches to connect' ) 
        opts.add_option( '--cluster', type='string', default=None, 
                         metavar='server1,server2...', 
                         help=( 'run on multiple servers (experimental!)' ) ) 
        opts.add_option( '--placement', type='choice', 
                         choices=list( PLACEMENT.keys() ), default='block', 
                         metavar='block|random', 
                         help=( 'node placement for --cluster ' 
                                '(experimental!) ' ) ) 
 
        self.options, self.args = opts.parse_args() 
 
        # We don't accept extra arguments after the options 
        if self.args: 
            opts.print_help() 
            exit() 
 
    def setup( self ): 
        "Setup and validate environment." 
 
        # set logging verbosity 
        if LEVELS[self.options.verbosity] > LEVELS['output']: 
            warn( '*** WARNING: selected verbosity level (%s) will hide CLI ' 
                    'output!\n' 
                    'Please restart Mininet with -v [debug, info, output].\n' 
                    % self.options.verbosity ) 
        lg.setLogLevel( self.options.verbosity ) 
 
    # Maybe we'll reorganize this someday... 
    # pylint: disable=too-many-branches,too-many-statements,global-statement 
 
    def begin( self ): 
        "Create and run mininet." 
 
        global CLI 
 
        opts = self.options 
 
        if opts.cluster: 
            servers = opts.cluster.split( ',' ) 
            for server in servers: 
                ClusterCleanup.add( server ) 
 
        if opts.clean: 
            cleanup() 
            exit() 
 
        start = time.time() 
 
        topo = MyTopology() 
        switch = customClass( SWITCHES, opts.switch ) 
        host = customClass( HOSTS, opts.host ) 
        controller = lambda name: RemoteController(name=name, ip='10.0.2.201', port=6653)
        link = customClass( LINKS, opts.link )
        listenPort = None
        if self.validate:
            self.validate( opts )
 
        if not opts.nolistenport:
            listenPort = opts.listenport

        Net = MininetWithControlNet if opts.innamespace else Mininet

        # Wait for controllers to connect unless we're running null test
        if ( opts.test and opts.test != [ 'none' ] and
             isinstance( opts.wait, bool ) ):
            opts.wait = True

 
        mn = Net( topo=topo, 
                  switch=switch, host=host, controller=controller, link=link, 
                  ipBase=opts.ipbase, inNamespace=opts.innamespace, 
                  xterms=opts.xterms, autoSetMacs=opts.mac, 
                  autoStaticArp=opts.arp, autoPinCpus=opts.pin, 
                  waitConnected=opts.wait, 
                  listenPort=listenPort ) 
         
        count = 1
        for s_from, s_to in sw_ext_intf_edges:
            S = name = None
            if s_from in [sw.name for sw in mn.switches]:
                S = mn[s_from]
                name = s_from
            else:
                S = mn[s_to]
                name = s_to
            if name == s_from:
                S.cmd(f"ip link add {name}-gre{count} type gretap local 12.12.12.{count} remote 14.14.14.{count} ttl 64")
                S.cmd(f"ip link set {name}-gre{count}")
                Intf(f"{name}-gre{count}", node=S)
            elif name == s_to:
                S.cmd(f"ip link add {name}-gre{count} type gretap local 14.14.14.{count} remote 12.12.12.{count} ttl 64")
                S.cmd(f"ip link set {name}-gre{count}")
                Intf(f"{name}-gre{count}", node=S)
            count += 1
 
        info('*** Note: you may need to reconfigure the interfaces for ' 
             'the Mininet hosts:\n', mn.hosts, '\n') 
 
        if opts.ensure_value( 'nat', False ): 
            with open( '/etc/resolv.conf' ) as f: 
                if 'nameserver 127.' in f.read(): 
                    warn( '*** Warning: loopback address in /etc/resolv.conf ' 
                          'may break host DNS over NAT\n') 
            mn.addNAT( *opts.nat_args, **opts.nat_kwargs ).configDefault() 
 
        # --custom files can set CLI or change mininet.cli.CLI 
        CLI = mininet.cli.CLI if CLI is None else CLI 
 
        if opts.pre: 
            CLI( mn, script=opts.pre ) 
 
        mn.start() 
 
        if opts.test: 
            runTests( mn, opts.test ) 
        else: 
            CLI( mn ) 
 
        if opts.post: 
            CLI( mn, script=opts.post ) 
 
        mn.stop() 
 
        elapsed = float( time.time() - start ) 
        info( 'completed in %0.3f seconds\n' % elapsed ) 
 
 
if __name__ == "__main__": 
    try: 
        MininetRunner() 
    except KeyboardInterrupt: 
        info( "\n\nKeyboard Interrupt. Shutting down and cleaning up...\n\n") 
        cleanup() 
    except Exception:  # pylint: disable=broad-except 
        # Print exception 
        type_, val_, trace_ = sys.exc_info() 
        errorMsg = ( "-"*80 + "\n" + 
                     "Caught exception. Cleaning up...\n\n" + 
                     "%s: %s\n" % ( type_.__name__, val_ ) + 
                     "-"*80 + "\n" ) 
        error( errorMsg ) 
        # Print stack trace to debug log 
        import traceback 
        stackTrace = traceback.format_exc() 
        debug( stackTrace + "\n" ) 
        cleanup()
