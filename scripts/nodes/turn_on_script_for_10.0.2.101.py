#!/usr/bin/env python
#new
import os
import sys
import time

from functools import partial
from optparse import OptionParser  # pylint: disable=deprecated-module
from sys import exit  # pylint: disable=redefined-builtin

# Fix setuptools' evil madness, and open up (more?) security holes
if 'PYTHONPATH' in os.environ:
    sys.path = os.environ['PYTHONPATH'].split(':') + sys.path

# pylint: disable=wrong-import-position

from mininet.clean import cleanup
import mininet.cli
from mininet.log import lg, LEVELS, info, debug, warn, error, output
from mininet.net import Mininet, MininetWithControlNet, VERSION
from mininet.node import (Host, CPULimitedHost, Controller, OVSController,
                          Ryu, NOX, RemoteController, findController,
                          DefaultController, NullController,
                          UserSwitch, OVSSwitch, OVSBridge, OVSKernelSwitch,
                          IVSSwitch)
from mininet.nodelib import LinuxBridge
from mininet.link import Link, TCLink, TCULink, OVSLink
from mininet.topo import (Topo, SingleSwitchTopo, LinearTopo,
                          SingleSwitchReversedTopo, MinimalTopo)
from mininet.topolib import TreeTopo, TorusTopo
from mininet.util import customClass, specialClass, splitArgs, buildTopo

sw_ext_intf = ['s0', 's12']


class MyTopo(Topo):
    "Auto generated topology for this Mininet Node"

    def __init__(self):
        Topo.__init__(self)

        "Add hosts and swiches"
        s0 = self.addSwitch('s0')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        h3 = self.addHost('h3', ip='1.2.3.1/16')
        s6 = self.addSwitch('s6')
        h11 = self.addHost('h11', ip='1.2.3.2/16')
        h8 = self.addHost('h8', ip='1.2.3.3/16')
        h9 = self.addHost('h9', ip='1.2.3.4/16')
        h7 = self.addHost('h7', ip='1.2.3.5/16')
        s10 = self.addSwitch('s10')
        h15 = self.addHost('h15', ip='1.2.3.6/16')

        "Add links"
        self.addLink(s0, s1)
        self.addLink(s0, s2)
        self.addLink(s0, s4)
        self.addLink(s0, s5)
        self.addLink(s1, h3)
        self.addLink(s2, s6)
        self.addLink(s4, h11)
        self.addLink(s5, h8)
        self.addLink(s5, h9)
        self.addLink(s5, h7)
        self.addLink(s6, s10)
        self.addLink(s10, h15)


def checkIntf(intf):
    "Make sure intf exists and is not configured."
    config = quietRun('ifconfig %s 2>/dev/null' % intf, shell=True)
    if not config:
        error('Error:', intf, 'does not exist!\n')
        exit(1)
    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', config)
    if ips:
        error('Error:', intf, 'has an IP address,'
                              'and is probably in use!\n')
        exit(1)


# built in topologies, created only when run
TOPODEF = 'minimal'
TOPOS = {'minimal': MinimalTopo,
         'linear': LinearTopo,
         'reversed': SingleSwitchReversedTopo,
         'single': SingleSwitchTopo,
         'tree': TreeTopo,
         'torus': TorusTopo}

SWITCHDEF = 'ovsk'
SWITCHES = {'user': UserSwitch,
            'ovs': OVSSwitch,
            'ovsk': OVSKernelSwitch,
            'ovsbr': OVSBridge,
            # Keep ovsk for compatibility with 2.0
            'ivs': IVSSwitch,
            'lxbr': LinuxBridge,
            'default': OVSSwitch}

HOSTDEF = 'proc'
HOSTS = {'proc': Host,
         'rt': specialClass(CPULimitedHost, defaults=dict(sched='rt')),
         'cfs': specialClass(CPULimitedHost, defaults=dict(sched='cfs'))}

CONTROLLERDEF = 'ovsc'
CONTROLLERS = {'ref': Controller,
               'ovsc': OVSController,
               'nox': NOX,
               'remote': RemoteController,
               'ryu': Ryu,
               'default': DefaultController,  # Note: overridden below
               'none': NullController}

LINKDEF = 'default'
LINKS = {'default': Link,  # Note: overridden below
         'tc': TCLink,
         'tcu': TCULink,
         'ovs': OVSLink}

# optional tests to run
TESTS = ['cli', 'build', 'pingall', 'pingpair', 'iperf', 'all', 'iperfudp',
         'none']

ALTSPELLING = {'pingall': 'pingAll', 'pingpair': 'pingPair',
               'iperfudp': 'iperfUdp'}


def addDictOption(opts, choicesDict, default, name, **kwargs):
    """Convenience function to add choices dicts to OptionParser.
       opts: OptionParser instance
       choicesDict: dictionary of valid choices, must include default
       default: default choice key
       name: long option name
       kwargs: additional arguments to add_option"""
    helpStr = ('|'.join(sorted(choicesDict.keys())) +
               '[,param=value...]')
    helpList = ['%s=%s' % (k, v.__name__)
                for k, v in choicesDict.items()]
    helpStr += ' ' + (' '.join(helpList))
    params = dict(type='string', default=default, help=helpStr)
    params.update(**kwargs)
    opts.add_option('--' + name, **params)


def version(*_args):
    "Print Mininet version and exit"
    output("%s\n" % VERSION)
    exit()


class MininetRunner(object):
    "Build, setup, and run Mininet."

    def __init__(self):
        "Init."
        self.options = None
        self.args = None  # May be used someday for more CLI scripts
        self.validate = None

        self.parseArgs()
        self.setup()
        self.begin()

    def custom(self, _option, _opt_str, value, _parser):
        """Parse custom file and add params.
           option: option e.g. --custom
           opt_str: option string e.g. --custom
           value: the value the follows the option
           parser: option parser instance"""
        files = []
        if os.path.isfile(value):
            # Accept any single file (including those with commas)
            files.append(value)
        else:
            # Accept a comma-separated list of filenames
            files += value.split(',')

        for fileName in files:
            customs = {}
            if os.path.isfile(fileName):
                # pylint: disable=exec-used
                with open(fileName) as f:
                    exec(compile(f.read(), fileName, 'exec'),
                         customs, customs)
                for name, val in customs.items():
                    self.setCustom(name, val)
            else:
                raise Exception('could not find custom file: %s' % fileName)

    def setCustom(self, name, value):
        "Set custom parameters for MininetRunner."
        if name in ('topos', 'switches', 'hosts', 'controllers', 'links'
                                                                 'testnames', 'tests'):
            # Update dictionaries
            param = name.upper()
            globals()[param].update(value)
        elif name == 'validate':
            # Add custom validate function
            self.validate = value
        else:
            # Add or modify global variable or class
            globals()[name] = value

    def setNat(self, _option, opt_str, value, parser):
        "Set NAT option(s)"
        assert self  # satisfy pylint
        parser.values.nat = True
        # first arg, first char != '-'
        if parser.rargs and parser.rargs[0][0] != '-':
            value = parser.rargs.pop(0)
            _, args, kwargs = splitArgs(opt_str + ',' + value)
            parser.values.nat_args = args
            parser.values.nat_kwargs = kwargs
        else:
            parser.values.nat_args = []
            parser.values.nat_kwargs = {}

    def parseArgs(self):
        """Parse command-line args and return options object.
           returns: opts parse options dict"""

        desc = ("The %prog utility creates Mininet network from the\n"
                "command line. It can create parametrized topologies,\n"
                "invoke the Mininet CLI, and run tests.")

        usage = ('%prog [options]\n'
                 '(type %prog -h for details)')

        opts = OptionParser(description=desc, usage=usage)
        addDictOption(opts, SWITCHES, SWITCHDEF, 'switch')
        addDictOption(opts, HOSTS, HOSTDEF, 'host')
        addDictOption(opts, CONTROLLERS, [], 'controller', action='append')
        addDictOption(opts, LINKS, LINKDEF, 'link')
        addDictOption(opts, TOPOS, TOPODEF, 'topo')

        opts.add_option('--clean', '-c', action='store_true',
                        default=False, help='clean and exit')
        opts.add_option('--custom', action='callback',
                        callback=self.custom,
                        type='string',
                        help='read custom classes or params from .py file(s)'
                        )
        opts.add_option('--test', default=[], action='append',
                        dest='test', help='|'.join(TESTS.keys()))
        opts.add_option('--xterms', '-x', action='store_true',
                        default=False, help='spawn xterms for each node')
        opts.add_option('--ipbase', '-i', type='string', default='10.0.0.0/8',
                        help='base IP address for hosts')
        opts.add_option('--mac', action='store_true',
                        default=False, help='automatically set host MACs')
        opts.add_option('--arp', action='store_true',
                        default=False, help='set all-pairs ARP entries')
        opts.add_option('--verbosity', '-v', type='choice',
                        choices=list(LEVELS.keys()), default='info',
                        help='|'.join(LEVELS.keys()))
        opts.add_option('--innamespace', action='store_true',
                        default=False, help='sw and ctrl in namespace?')
        opts.add_option('--listenport', type='int', default=6654,
                        help='base port for passive switch listening')
        opts.add_option('--nolistenport', action='store_true',
                        default=False, help="don't use passive listening " +
                                            "port")
        opts.add_option('--pre', type='string', default=None,
                        help='CLI script to run before tests')
        opts.add_option('--post', type='string', default=None,
                        help='CLI script to run after tests')
        opts.add_option('--pin', action='store_true',
                        default=False, help="pin hosts to CPU cores "
                                            "(requires --host cfs or --host rt)")
        opts.add_option('--nat', action='callback', callback=self.setNat,
                        help="[option=val...] adds a NAT to the topology that"
                             " connects Mininet hosts to the physical network."
                             " Warning: This may route any traffic on the machine"
                             " that uses Mininet's"
                             " IP subnet into the Mininet network."
                             " If you need to change"
                             " Mininet's IP subnet, see the --ipbase option.")
        opts.add_option('--version', action='callback', callback=version,
                        help='prints the version and exits')
        opts.add_option('--wait', '-w', action='store_true',
                        default=False, help='wait for switches to connect')
        opts.add_option('--twait', '-t', action='store', type='int',
                        dest='wait',
                        help='timed wait (s) for switches to connect')
        opts.add_option('--cluster', type='string', default=None,
                        metavar='server1,server2...',
                        help=('run on multiple servers (experimental!)'))
        opts.add_option('--placement', type='choice',
                        choices=list(PLACEMENT.keys()), default='block',
                        metavar='block|random',
                        help=('node placement for --cluster '
                              '(experimental!) '))

        self.options, self.args = opts.parse_args()

        # We don't accept extra arguments after the options
        if self.args:
            opts.print_help()
            exit()

    def setup(self):
        "Setup and validate environment."

        # set logging verbosity
        if LEVELS[self.options.verbosity] > LEVELS['output']:
            warn('*** WARNING: selected verbosity level (%s) will hide CLI '
                 'output!\n'
                 'Please restart Mininet with -v [debug, info, output].\n'
                 % self.options.verbosity)
        lg.setLogLevel(self.options.verbosity)

    # Maybe we'll reorganize this someday...
    # pylint: disable=too-many-branches,too-many-statements,global-statement

    def begin(self):
        "Create and run mininet."

        opts = self.options

        if opts.clean:
            cleanup()
            exit()

        start = time.time()

        topo = MyTopo()
        switch = addSwitch(opts.switch)
        host = addHost(opts.host)
        controller = lambda name: RemoteController(name, ip='10.0.2.201', port=int('6533'))
        link = addLink(opts.link)

        if self.validate:
            self.validate(opts)

        inNamespace = self.options.innamespace
        Net = Mininet if not inNamespace else MininetWithControlNet

        ipBase = opts.ipbase
        xterms = opts.xterms
        mac = opts.mac
        arp = opts.arp
        pin = opts.pin
        listenPort = None
        if not opts.nolistenport:
            listenPort = opts.listenport

        intfName = 'eth1'
        info('*** Checking', intfName, '\n')
        checkIntf(intfName)

        mn = Net(topo=topo,
                 switch=switch, host=host, controller=controller,
                 link=link,
                 ipBase=ipBase,
                 inNamespace=inNamespace,
                 xterms=xterms, autoSetMacs=mac,
                 autoStaticArp=arp, autoPinCpus=pin,
                 listenPort=listenPort, services=True)

        for sw in mn.switches:
            if sw.name in sw_ext_intf:
                info('*** Adding hardware interface', intfName, 'to switch',
                     sw.name, '\n')
                _intf = Intf(intfName, node=sw)

        info('*** Note: you may need to reconfigure the interfaces for '
             'the Mininet hosts:\n', mn.hosts, '\n')

        if opts.pre:
            CLI(mn, script=self.options.pre)

        test = opts.test
        test = ALTSPELLING.get(test, test)

        mn.start()

        if test == 'none':
            pass
        elif test == 'all':
            mn.start()
            mn.ping()
            mn.iperf()
        elif test == 'cli':
            CLI(mn)
        elif test != 'build':
            getattr(mn, test)()

        if opts.post:
            CLI(mn, script=self.options.post)

        mn.stop()

        elapsed = float(time.time() - start)
        info('completed in %0.3f seconds\n' % elapsed)


if __name__ == "__main__":
    MininetRunner()
