import sys
sys.path.append("operating_system")
from kernel import Kernel
from dispatcher import NoMoreProcesses
from hardware.machine import Machine
import config
import program_generation
import process_statistics

TRACE_FILE= "process_trace.txt"
STAT_FILE= "statistics.txt"

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
program_durations= dict([ (program.pid, program.duration) for program in programs])

my_os.kickstart()

for cycle in xrange(10**8): #run for a maximum of 10^8 cycles, for sanity's sake
    if cycle%1000==0:
        print "executing simulation: cycle ", cycle
    if cycle== cfg.runtime:
        print "reached simulation runtime. Simulation stopped."
        break
    try:
        my_pc.step()
    except NoMoreProcesses:
        print "At cycle",cycle, "all processes have finished. Simulation stopped"
        break

my_os.shutdown()

tracer.process(program_durations)
print "writing process trace to "+TRACE_FILE+" (PID 0 is the idle process)"
open(TRACE_FILE, "w").write( str(tracer) )
print "writing statistics to "+STAT_FILE
open(STAT_FILE, "w").write( tracer.get_statistics(cfg.iotime, program_durations) )
