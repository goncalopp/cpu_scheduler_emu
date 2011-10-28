from ram_cell import RamCell, Instruction
import cpu_interrupt
import logging
log= logging.getLogger('hardware')

K=1024
M= 1024*K

OS_MEMORY_START=      128
PROGRAM_MEMORY_START= 1*K

'''
RAM CONTENTS:
0    - 127 :    interrupt vector
128  - 1023:    reserved
1024 - X   :    available
'''

class RAM:
    def __init__(self, size):
        assert size >= 100*K
        self.contents= [ RamCell(0) for i in xrange(size) ]

    def read(self, position):
        return self.raw_read(position).op

    def write(self, position, content):
        self.raw_write( position, RamCell(content) )

    def raw_read(self, position):
        return self.contents[position]

    def raw_write(self, position, content):
        assert isinstance(content, RamCell)
        self.contents[position]= content

    def __len__(self):
        return len(self.contents)
    def __getitem__(self, i):
        if type(i)==int:
            return self.read(i)
        elif type(i)==slice:
            return [self.read(x) for x in xrange(*i.indices(len(self.contents)))]
        else:
            raise NotImplemented()

    def __setitem__(self, i, x):
        self.write(i,x)

    def _write_interrupt_handler(self, n, ih):
        assert type(n)==int
        assert isinstance(ih, cpu_interrupt.InterruptHandler)
        self[n]= ih 

    def _read_interrupt_handler(self, n):
        assert type(n)==int
        ih= self[n]
        assert isinstance(ih, cpu_interrupt.InterruptHandler)
        return ih
