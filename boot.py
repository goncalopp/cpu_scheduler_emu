import sys

sys.path.append("os")
sys.path.append("os/hardware")
from operating_system import OS
from machine import Machine
import cpu

my_pc= Machine( 100 )
my_os= OS( my_pc )
while True:
    try:
        my_pc.step()
    except cpu.Poweroff:
        print "execution finished"
        break
