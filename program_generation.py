import sys
sys.path.append("operating_system")
from hardware.cpu_instruction import Instruction, Program, NOOP, INT
import config
import random

IO_INTERRUPT_NUMBER= 2

def generateProgramsFromConfig( c ):
    '''generates programs (sequences of instructions) from simulation configuration information'''
    assert isinstance(c, config.SimConfig)
    programs=[]
    for i in xrange(c.numprocess):
        programduration= random.normalvariate( c.meandev, c.standdev )
        cpu_burst= c.bursts[i]
        instructions= []
        while len(instructions) < c.runtime: #at most, a this program will run for the whole duration of the simulation
            instructions.extend( [Instruction(NOOP)]*cpu_burst ) #burn cpu doing nothing...
            instructions.append( Instruction( INT, IO_INTERRUPT_NUMBER) )    #and do IO operation
        programs.append( Program(instructions) )
    return programs
