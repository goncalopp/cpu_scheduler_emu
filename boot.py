import sys,os
from kernel import Kernel
from dispatcher import NoMoreProcesses
from hardware.machine import Machine
import process_statistics
import program_generation

MAX_CYCLES= 10**8 #run for a maximum of 10^8 cycles, for sanity's sake
TRACE_FILE= "process_trace.txt"
STAT_FILE= "statistics.txt"

def simulate(programs=[], config=None):
    if not config is None:
        io_times= config.iotimes
        runtime= config.runtime
        generator= program_generation.ProgramGenerator( config )
        print "generating and assembling programs (from config)"
        programs= generator.generate_initial_programs()
    else:
        io_times=[100]
        runtime= MAX_CYCLES
        generator= None
    
    print "creating virtual hardware"
    number_of_ios= len(io_times)
    number_of_syscalls= number_of_ios+1
    my_pc= Machine( number_of_ios, number_of_syscalls, io_times )
    print '"bootstraping" OS'
    my_os= Kernel( my_pc )
    tracer= process_statistics.ProcessTracer( my_os )   #traces processes

    print "creating processes"
    for program in programs:
        pcb= my_os.process_manager.start_program( program )
        program.pid= pcb.pid    #hack to save the pid of each program (for calculating statistics)
        program.process_start_address= pcb.start_address    #hack for correctness tests
        if not hasattr(program, "duration"):
            program.duration=-1
        program.duration+=1     #since the programs are added one instruction by the OS (to signal termination)
    program_durations= dict([ (program.pid, program.duration) for program in programs])

    print "starting simulation"
    my_os.kickstart()

    for cycle in xrange( MAX_CYCLES): 
        if cycle%1000==0:
            print "executing simulation: cycle ", cycle
        if cycle== runtime:
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
    stats= tracer.get_statistics( [io.used_clocks for io in my_pc.ios], program_durations)
    #print stats[:200]   #only first 200 chars
    open(STAT_FILE, "w").write( stats )
    print "Additional execution information can be found in the debug logs (os.log.tsv, hardware.log.tsv)"
    print "plotting process progress graph"
    try:
        tracer.plot(show=True, to_file="process_progress.ps")
    except:
        print "Error showing plot. is python-gnuplot not installed? Continuing happil y"
    return my_pc, my_os #needed for correctness testing, since it checks final ram contents



