import sys
sys.path.append("operating_system")
from kernel import Kernel
from hardware.machine import Machine
from hardware.cpu import Poweroff

my_pc= Machine( 100 )
my_os= Kernel( my_pc )
while True:
    try:
        my_pc.step()
    except Poweroff:
        print "execution finished"
        break
