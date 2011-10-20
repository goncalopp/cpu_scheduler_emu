import sys

sys.path.append("os")
sys.path.append("os/hardware")
import operating_system
from machine import Machine
import cpu

my_pc= Machine( 100 )
operating_system.setup_interrupt_vector( my_pc )

while True:
    try:
        my_pc.step()
    except cpu.NoTask:
        print "execution finished (cpu has no task)"
        break
