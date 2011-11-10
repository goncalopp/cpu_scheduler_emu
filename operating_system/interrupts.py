import logging
log= logging.getLogger('os')
from hardware import machine

interrupt_list= ["timer", "syscall_end_process"]+ \
["io"+str(x) for x in range(machine.NUMBER_OF_IO_DEVICES)]+ \
["syscall_io_driver"+str(x) for x in range(machine.NUMBER_OF_IO_DEVICES)]

interrupt_numbers=  \
    {
    "timer":                machine.TIMER_INTERRUPT,
    "syscall_end_process":  machine.SYSCALL_INTERRUPT(0),
    }
interrupt_numbers.update( dict( [("io"+str(x), machine.IO_INTERRUPT(x)) for x in range(machine.NUMBER_OF_IO_DEVICES)]))
interrupt_numbers.update( dict( [("syscall_io_driver"+str(x), machine.SYSCALL_INTERRUPT(x+1)) for x in range(machine.NUMBER_OF_IO_DEVICES)]))


interrupt_durations= dict( [(k,0) for k in interrupt_list] )    #all 0
    
class InterruptHandlerProblem( Exception ):
    pass

class InterruptHandlerGroup:
    '''registers interrupt handlers, mapping them to OS functions'''
    def __init__(self, os, machine, os_functions):
        for name in interrupt_list:
            log.debug("registering interrupt handler: "+name)
            try:
                os_f= os_functions[name]
                n= interrupt_numbers[name]
                d= interrupt_durations[name]
                machine.set_interrupt_handler( n, d, os_f)
            except KeyError:
                raise InterruptHandlerProblem(name)

            
