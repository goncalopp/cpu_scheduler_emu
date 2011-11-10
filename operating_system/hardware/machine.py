import time
import logging
log= logging.getLogger('hardware')
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t%(module)s\t%(funcName)s\t%(message)s')
hdlr = logging.FileHandler('hardware.log.tsv', mode="w")
hdlr.setFormatter(formatter)
log.addHandler(hdlr) 
log.setLevel(logging.DEBUG)
import cpu, timer, io_device, ram


TIMER_INTERRUPT=        0
MEMORY_SIZE= 100*ram.K

class Machine:
    def __init__(self, io_devices_number, syscalls_number):
        self.NUMBER_OF_IO_DEVICES= io_devices_number
        self.NUMBER_OF_SYSCALLS= syscalls_number
        self.NUMBER_OF_INTERRUPTS= 1 + self.NUMBER_OF_IO_DEVICES + self.NUMBER_OF_SYSCALLS
        self.INTERRUPT_PRIORITIES= [2]+[0]*self.NUMBER_OF_IO_DEVICES+[1]*self.NUMBER_OF_SYSCALLS

        initial_interrupt_vector= [cpu.InterruptHandler(n, 0, lambda:None) for n in range(self.NUMBER_OF_INTERRUPTS)]
        self.ram= ram.RAM( MEMORY_SIZE )
        self.cpu= cpu.Cpu( self.ram )
        self.timer= timer.Timer( self.cpu, TIMER_INTERRUPT )
        self.ios= [io_device.IO( self.cpu, self.IO_INTERRUPT(x)) for x in range(self.NUMBER_OF_IO_DEVICES)]
        
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

    def IO_INTERRUPT(self, x):
        assert 0<=x<self.NUMBER_OF_IO_DEVICES
        return 1+x

    def SYSCALL_INTERRUPT(self, x):
        assert 0<=x<=self.NUMBER_OF_SYSCALLS
        return 1+self.NUMBER_OF_IO_DEVICES+x
