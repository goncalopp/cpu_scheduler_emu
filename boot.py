import sys
sys.path.append("operating_system")
from kernel import Kernel
from hardware.machine import Machine
from hardware.cpu import Poweroff
import config
import program_generation

cfg= config.configFromFile("configs/example_config.cfg")
programs= program_generation.generateProgramsFromConfig(cfg)


my_pc= Machine()
my_pc.io.set_io_operation_time( cfg.iotime )
my_os= Kernel( my_pc )

while True:
    try:
        my_pc.step()
    except Poweroff:
        print "execution finished"
        break
