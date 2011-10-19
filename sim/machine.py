NUMBER_OF_INTERRUPTS= 2

TIMER_INTERRUPT=    0
IO_INTERRUPT=       1

TIMER_INTERRUPT_DURATION=   0
IO_INTERRUPT_DURATION=      0

import cpu
import timer


class Machine:
    def __init__(self):
        initial_interrupt_vector= [cpu.Interrupt(n, 0, lambda:None) for n in range(NUMBER_OF_INTERRUPTS)]
        self.cpu= cpu.Cpu( initial_interrupt_vector )
        self.timer= timer.Timer( self.cpu, TIMER_INTERRUPT )
        
    def step(self):
        self.cpu.step()
        self.timer.step()

    def set_interrupt( self, *args, **kwargs ):
        self.cpu.set_interrupt( *args, **kwargs)
    
