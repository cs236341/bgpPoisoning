from router import Router

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from time import sleep


import os

sleepytime = 3

class BgpPoisoningTopo ( Topo ):

    def build ( self ):
        r1 = self.addSwitch ('R1', cls=Router )
        r2 = self.addSwitch ('R2', cls=Router )
        r3 = self.addSwitch ('R3', cls=Router )
        r4 = self.addSwitch ('R4', cls=Router )
        r5 = self.addSwitch ('R5', cls=Router )
        r6 = self.addSwitch ('R6', cls=Router )
        r7 = self.addSwitch ('R7', cls=Router )


        for h, s in [ (r1, r2), (r2, r3), (r3, r4), (r4, r5), (r2, r6), (r6,r7), (r7, r4) ]:
            self.addLink( h, s )



def run():
    #clean previous run
    
    os.system("rm -f  /tmp/*.pid logs/*")
    os.system("mn -c >/dev/null 2>&1")
    os.system("killall -9 zebra bgpd > /dev/null 2>&1")
    os.system("/etc/init.d/quagga restart")

    topo = BgpPoisoningTopo()
    net = Mininet( topo=topo )
    net.start()
    
    for router in net.switches:
        router.cmd("sysctl -w net.ipv4.ip_forward=1")
        router.waitOutput()

    #Waiting (sleepytime) seconds for sysctl changes to take effect..
    sleep(sleepytime)

    for R in ['R1','R2','R3','R4','R5','R6','R7']:
        net.get(R).initZebra("conf/zebra-%s.conf" % R)
        router.waitOutput()
        net.get(R).initBgpd("conf/bgpd-%s.conf" % R)
        router.waitOutput()
    
    CLI( net )
    net.stop()

if __name__== '__main__':
    setLogLevel( 'info' )
    run()
