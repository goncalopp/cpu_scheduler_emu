from cpu_instruction import Instruction, Program, OFF
import cpu_interrupt
import logging
log= logging.getLogger('hardware')

K=1024
M= 1024*K

'''
RAM CONTENTS:
0    - 127 :    interrupt vector
128  - 1023:    reserved
1024 - X   :    available
'''

class RAM:
    def __init__(self, size):
        assert size >= 100*K
        self.contents= [ Instruction(OFF, 0) for i in xrange(size) ]

    def read(self, position):
        return self.contents[position]

    def write(self, position, instruction):
        assert isinstance(instruction, Instruction)
        self.contents[position]=instruction

    def _write_interrupt_handler(self, n, ih):
        assert type(n)==int
        assert isinstance(ih, cpu_interrupt.Interrupt)
        self.write( n, Instruction(ih, 0) )

    def writeProgram(self, offset, program):
        assert isinstance(program, Program)
        for i,instruction in enumerate(program.instructions):
            self.write(offset+i, instruction)

    def _read_interrupt_handler(self, n):
        assert type(n)==int
        ih= self.read(n).op
        assert isinstance(ih, cpu_interrupt.Interrupt)
        return ih 
    
