import sys,os
sys.path.append("operating_system")
from kernel import Kernel
from dispatcher import NoMoreProcesses
from hardware.machine import Machine
import config
import program_generation
import process_statistics

def cli_choice(question, answers):
    n= len(answers)
    print question
    for i,answer in enumerate(answers):
        print str(i+1)+")\t"+answer
    while True:
        print ">",
        try:
            return answers[int(raw_input())-1]
        except (ValueError, IndexError):
            print "Invalid choice"

TRACE_FILE= "process_trace.txt"
STAT_FILE= "statistics.txt"
CONFIG_DIR= "configs"

config_files= os.listdir("configs")
#cfg_file= cli_choice( "Please choose the config file to use:",config_files )
cfg_file= "ten_processes.cfg" #uncomment here and comment previous line for no prompts 

print "parsing config file"
cfg= config.configFromFile( os.path.join( CONFIG_DIR, cfg_file ))
print "generating programs"
programs= program_generation.generateProgramsFromConfig(cfg)

print "creating virtual hardware"
my_pc= Machine()
my_pc.io.set_io_operation_time( cfg.iotime )
print '"bootstraping" OS'
my_os= Kernel( my_pc )
tracer= process_statistics.ProcessTracer( my_os )   #traces processes

print "creating processes"
for program in programs:
    pcb= my_os.process_manager.start_program( program )
    program.pid= pcb.pid    #hack to save the pid of each program (for calculating statistics)
    program.duration+=1     #since the programs are added one instruction by the OS (to signal termination)
program_durations= dict([ (program.pid, program.duration) for program in programs])

print "starting simulation"
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
trace= str(tracer)
#print trace
open(TRACE_FILE, "w").write( trace )
print "writing statistics to "+STAT_FILE
stats= tracer.get_statistics(cfg.iotime, program_durations)
print stats[:200]   #only first 200 chars
open(STAT_FILE, "w").write( stats )
