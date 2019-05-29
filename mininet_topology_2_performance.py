#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=2 ):
    controller = self.addRemoteController( 'c0')
	switch = self.addSwitch( 's1' )
	for h in range(n):
	    # Each host gets 50%/n of system CPU
	    host = self.addHost( 'h%s' % (h + 1),
		                 cpu= 1)
	    # 10 Mbps, 5ms delay, 2% loss, 1000 packet queue
	    self.addLink( host, switch, bw=0.5, delay='0ms', loss=0,
                          max_queue_size=0, use_htb=True )

def perfTest():
    "Create network and run simple performance test"
    topo = SingleSwitchTopo( n=4 )
    net = Mininet( topo=topo,
	           host=CPULimitedHost, link=TCLink )
    net.start()
    print "Dumping host connections"
    dumpNodeConnections( net.hosts )
    print "Testing network connectivity"
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()
