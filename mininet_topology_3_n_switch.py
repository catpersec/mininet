#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch
from mininet.node import Controller, RemoteController, OVSController
from mininet.topo import Topo
from mininet.log import lg, info
from mininet.util import irange, quietRun
from mininet.link import TCLink
from functools import partial
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

import sys
flush = sys.stdout.flush

class LinearTestTopo( Topo ):
    "Topology for a string of N hosts and N-1 switches."

    def build( self, N, **params ):
        # Create switches and hosts

        hosts = [ self.addHost( 'h%s' % h )
                  for h in irange( 1, N ) ]
        switches = [ self.addSwitch( 's%s' % s )
                     for s in irange( 1, N - 1 ) ]

        # Wire up switches
        last = None
        for switch in switches:
            if last:
                self.addLink( last, switch )
            last = switch

        # Wire up hosts
        self.addLink( hosts[ 0 ], switches[ 0 ] )
        for host, switch in zip( hosts[ 1: ], switches ):
            self.addLink( host, switch )


def linearBandwidthTest( lengths ):

    "Check bandwidth at various lengths along a switch chain."

    results = {}
    switchCount = max( lengths )
    hostCount = switchCount + 1

    switches = { 'reference user': UserSwitch,
                 'Open vSwitch kernel': OVSKernelSwitch }

    # UserSwitch is horribly slow with recent kernels.
    # We can reinstate it once its performance is fixed
    del switches[ 'reference user' ]

    topo = LinearTestTopo( hostCount )

    # Select TCP Reno
    output = quietRun( 'sysctl -w net.ipv4.tcp_congestion_control=reno' )
    assert 'reno' in output

    for datapath in switches.keys():
        info( "*** testing", datapath, "datapath\n" )
        Switch = switches[ datapath ]
        results[ datapath ] = []
        link = partial( TCLink, bw=0.3 )
        net = Mininet( topo=topo, switch=Switch,
                        controller=RemoteController,
                       link=link )
        net.start()
        CLI(net)
        net.stop()

    for datapath in switches.keys():
        info( "\n*** Linear network results for", datapath, "datapath:\n" )
        result = results[ datapath ]
        info( "SwitchCount\tiperf Results\n" )
        for switchCount, serverbw in result:
            info( switchCount, '\t\t' )
            info( serverbw, '\n' )
        info( '\n')
    info( '\n' )
#How many switches?
if __name__ == '__main__':
    lg.setLogLevel( 'info' )
    sizes = [ 1, 3 ]
    info( "*** Running linearBandwidthTest", sizes, '\n' )
    linearBandwidthTest( sizes )
