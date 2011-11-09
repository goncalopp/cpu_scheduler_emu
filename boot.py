import sys
sys.path.append("operating_system")
from kernel import Kernel
from dispatcher import NoMoreProcesses
from hardware.machine import Machine
from hardware.cpu import Poweroff
import config
import program_generation
import process_statistics

cfg= config.configFromFile("configs/example_config.cfg")
programs= program_generation.generateProgramsFromConfig(cfg)

my_pc= Machine()
my_pc.io.set_io_operation_time( cfg.iotime )
my_os= Kernel( my_pc )
tracer= process_statistics.ProcessTracer( my_os )

for program in programs:
    pcb= my_os.process_manager.start_program( program )
    program.pid= pcb.pid    #hack to save the pid of each program (for calculating statistics)
    program.duration+=1     #since the programs are added one instruction by the OS (to signal termination)

my_os.kickstart()

for cycle in xrange(10**8):
    if cycle== cfg.runtime:
        print "reached simulation runtime"
        break
    try:
        my_pc.step()
    except NoMoreProcesses:
        print "All processes finished"
        break

my_os.shutdown()

program_durations= dict([ (program.pid, program.duration) for program in programs])
tracer.process(program_durations)
print tracer
print tracer.get_statistics(cfg.iotime, program_durations)
