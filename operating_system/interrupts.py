import logging
log= logging.getLogger('os')
from hardware import machine

interrupt_list= ["timer","io", "syscall_io_driver", "syscall_end_process"]

interrupt_numbers=  \
    {
    "timer":                machine.TIMER_INTERRUPT,
    "io":                   machine.IO_INTERRUPT,
    "syscall_io_driver":    machine.SYSCALL_INTERRUPT_1,
    "syscall_end_process":  machine.SYSCALL_INTERRUPT_2,
    }

interrupt_durations= \
    {
    "timer":                0,
    "io":                   0,
    "syscall_io_driver":    0,
    "syscall_end_process":  0,
    }
    
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

            
