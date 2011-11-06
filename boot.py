import sys
sys.path.append("operating_system")
from kernel import Kernel
from dispatcher import NoMoreProcesses
from hardware.machine import Machine
from hardware.cpu import Poweroff
import config
import program_generation

cfg= config.configFromFile("configs/example_config.cfg")
programs= program_generation.generateProgramsFromConfig(cfg)

my_pc= Machine()
my_pc.io.set_io_operation_time( cfg.iotime )
my_os= Kernel( my_pc )
for program in programs:
    my_os.process_manager.start_program( program )
my_os.kickstart()

for cycle in xrange(10**8):
    try:
        my_pc.step()
    except NoMoreProcesses:
        print "All processes finished"
        break
    if cycle== cfg.runtime:
        print "reached simulation runtime"
        break
