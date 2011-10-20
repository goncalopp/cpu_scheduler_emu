import sys
sys.path.append("os")
sys.path.append("os/hardware")
import operating_system
from machine import Machine

my_pc= Machine( 100 )
operating_system.setup_interrupt_vector( my_pc )

while True:
    my_pc.step()
