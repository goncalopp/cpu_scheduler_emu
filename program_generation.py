import sys
sys.path.append("operating_system")
from hardware.cpu_instruction import programFromString
import config
import random

class CannotGenerateProgram( Exception ):
    pass

IO_INTERRUPT_NUMBER= 2

BURN_CYCLES_INSTRUCTIONS='''
LOAD    {x}
ADD     -1
JNZ     -1
'''

def burn_cycles(n):
    if n<3:
        raise CannotGenerateProgram("Can't burn less than 3 cycles")
    x= int((n-3)/2 + 1)
    instructions= BURN_CYCLES_INSTRUCTIONS.format(x=x)
    if (n % 2)==1:
        #odd number
        return instructions
    else:
        #even number
        return "NOOP\n"+instructions

def generateProgram( program_duration, cpu_burst, io_int_number ):
    cpu_burst -=1   #since 1 IO operation consumes a clock
    instructions= ""
    left= program_duration
    while left>0: 
        burn= min(left, cpu_burst)
        instructions+= burn_cycles( burn )
        left -=burn
        if not left>0:
            break
        instructions+="INT "+str(io_int_number)+"\n"
        left -=1    #io operation burns one cpu clock too
    assert left==0
    return programFromString(instructions)

class ProgramGenerator:
    '''generates programs (sequences of instructions) from simulation configuration information'''
    def __init__(self, cfg ):
        assert isinstance(cfg, config.SimConfig)
        self.config= cfg

    def generate_program(self, i=0):    #if i(ndex) is not specified, take config from first
        c= self.config
        program_duration= int(random.normalvariate( c.meandev, c.standdev ))
        program_io_int= 1+c.iodevices +1+ c.process_ios[i] #timer int, io_devices int, and process termination syscall int
        cpu_burst= c.process_bursts[i]
        #print "generating program with duration",program_duration,"and cpu_burst",cpu_burst
        while True:
            try:
                program= generateProgram( program_duration, cpu_burst, program_io_int ) 
                break
            except CannotGenerateProgram:
                if c.standdev==0:
                    raise CannotGenerateProgram("I cannot generate a program with this number of cycles, and standdev is 0...")
                #print "couldn't generate program with given characteristics, trying again"
        program.duration= program_duration #hack to save the program duration, for process statistics
        return program

    def generate_initial_programs(self):
        return [self.generate_program(x) for x in range(self.config.numprocess)]
