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
    my_os.dispatcher.start_program( program )
my_os.kickstart()

while True:
    try:
        my_pc.step()
    except Poweroff:
        print "system has powered off"
        break
    except NoMoreProcesses:
        print "No more processes to execute"
        break
