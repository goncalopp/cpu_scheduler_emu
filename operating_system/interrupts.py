import logging
log= logging.getLogger('os')
from hardware import machine
  
class InterruptHandlerProblem( Exception ):
    pass

class InterruptHandlerGroup:
    '''registers interrupt handlers, mapping them to OS functions'''
    def __init__(self, os):
        self.os=os
        machine= os.machine
        self.interrupt_list= ["timer", "syscall_end_process"]+ \
        ["io"+str(x) for x in range(machine.NUMBER_OF_IO_DEVICES)]+ \
        ["syscall_io_driver"+str(x) for x in range(machine.NUMBER_OF_IO_DEVICES)]
        self.interrupt_numbers=  \
            {
            "timer":                machine.TIMER_INTERRUPT,
            "syscall_end_process":  machine.SYSCALL_INTERRUPT(0),
            }
        self.interrupt_numbers.update( dict( [("io"+str(x), machine.IO_INTERRUPT(x)) for x in range(machine.NUMBER_OF_IO_DEVICES)]))
        self.interrupt_numbers.update( dict( [("syscall_io_driver"+str(x), machine.SYSCALL_INTERRUPT(x+1)) for x in range(machine.NUMBER_OF_IO_DEVICES)]))
        self.interrupt_durations= dict( [(k,0) for k in self.interrupt_list] )    #all 0
        
    def set_handlers( self, handlers ):
        for name in self.interrupt_list:
            log.debug("registering interrupt handler: "+name)
            try:
                os_f= handlers[name]
                n= self.interrupt_numbers[name]
                d= self.interrupt_durations[name]
                self.os.machine.set_interrupt_handler( n, d, os_f)
            except KeyError:
                raise InterruptHandlerProblem(name)

            
