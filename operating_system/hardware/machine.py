import time
import logging
log= logging.getLogger('hardware')
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t%(module)s\t%(funcName)s\t%(message)s')
hdlr = logging.FileHandler('hardware.log.tsv', mode="w")
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.DEBUG)
import cpu, timer, io_device, ram

NUMBER_OF_IO_DEVICES=   5
NUMBER_OF_SYSCALLS=     4
TIMER_INTERRUPT=        0
def IO_INTERRUPT(x):
    assert 0<=x<NUMBER_OF_IO_DEVICES
    return 1+x
def SYSCALL_INTERRUPT(x):
    assert 0<=x<=NUMBER_OF_SYSCALLS
    return 1+NUMBER_OF_IO_DEVICES+x
NUMBER_OF_INTERRUPTS= 1 + NUMBER_OF_IO_DEVICES + NUMBER_OF_SYSCALLS
INTERRUPT_PRIORITIES= [2]+[0]*NUMBER_OF_IO_DEVICES+[1]*NUMBER_OF_SYSCALLS
MEMORY_SIZE= 100*ram.K

class Machine:
    def __init__(self):
        initial_interrupt_vector= [cpu.InterruptHandler(n, 0, lambda:None) for n in range(NUMBER_OF_INTERRUPTS)]
        self.ram= ram.RAM( MEMORY_SIZE )
        self.cpu= cpu.Cpu( self.ram )
        self.timer= timer.Timer( self.cpu, TIMER_INTERRUPT )
        self.ios= [io_device.IO( self.cpu, IO_INTERRUPT(x)) for x in range(NUMBER_OF_IO_DEVICES)]
        
    def step(self):
        #time.sleep(0.01)    #for making sense of log files
        self.cpu.step()
        self.timer.step()
        [io.step() for io in self.ios]

    def set_interrupt_handler( self, *args, **kwargs ):
        self.cpu.set_interrupt_handler( *args, **kwargs)

    def get_clock_ticks( self ):
        return self.cpu.registers.TSC
    
    def generate_interrupt( number ):
        log.debug("generated interrupt"+str(number))
        self.cpu.interrupt( number )

    def debug(self, memory_dump_address, memory_dump_size):
        '''returns debug information'''
        m1= memory_dump_address
        m2= m1+ memory_dump_size
        registers= str(self.cpu.registers)
        memory= "\n".join([str(self.ram.raw_read(x)) for x in xrange(m1, m2)])
        instruction= self.ram.raw_read( self.cpu.registers.PC )
        separator= "--------------------------------------------------"
        return "{separator}\n{memory}\n{registers}\n{instruction}".format(**locals())
