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

def generateProgram( program_duration, cpu_burst ):
    cpu_burst -=1   #since 1 IO operation consumes a clock
    instructions= ""
    left= program_duration
    while left>0: 
        burn= min(left, cpu_burst)
        instructions+= burn_cycles( burn )
        left -=burn
        if not left>0:
            break
        instructions+="INT 2\n"
        left -=1    #io operation burns one cpu clock too
    if left!=0:
        raise CannotGenerateProgram("Failed to generate program with given number of instructions")
    return programFromString(instructions)

def generateProgramsFromConfig( c ):
    '''generates programs (sequences of instructions) from simulation configuration information'''
    assert isinstance(c, config.SimConfig)
    programs=[]
    for i in xrange(c.numprocess):
        while True:
            program_duration= int(random.normalvariate( c.meandev, c.standdev ))
            cpu_burst= c.bursts[i]
            print "generating program with duration",program_duration,"and cpu_burst",cpu_burst
            try:
                program= generateProgram( program_duration, cpu_burst )
                break
            except CannotGenerateProgram:
                print "couldn't generate program with given characteristics, trying again"
        programs.append( program )
    return programs
