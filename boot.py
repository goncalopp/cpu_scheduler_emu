import sys

sys.path.append("os")
sys.path.append("os/hardware")
from operating_system import OS
from machine import Machine
import cpu

my_pc= Machine( 100 )
my_os= OS( my_pc )
my_os.setup_interrupt_vector()

while True:
    try:
        my_pc.step()
    except cpu.NoTask:
        print "execution finished (cpu has no task)"
        break
