import cpu
import timer

NUMBER_OF_INTERRUPTS= 6

TIMER_INTERRUPT=     0
IO_INTERRUPT=        1
SYSCALL_INTERRUPT_1= 2
SYSCALL_INTERRUPT_2= 3
SYSCALL_INTERRUPT_3= 4
SYSCALL_INTERRUPT_4= 5

class Machine:
    def __init__(self):
        initial_interrupt_vector= [cpu.Interrupt(n, 0, lambda:None) for n in range(NUMBER_OF_INTERRUPTS)]
        self.cpu= cpu.Cpu( initial_interrupt_vector )
        self.timer= timer.Timer( self.cpu, TIMER_INTERRUPT )
        
    def step(self):
        self.cpu.step()
        self.timer.step()

    def set_interrupt_handler( self, *args, **kwargs ):
        self.cpu.set_interrupt_handler( *args, **kwargs)

    def get_clock_ticks():
        return self.cpu.tsc()
    
