import machine
import cpu

m= machine.Machine( 100 )

m.set_interrupt_handler( machine.TIMER_INTERRUPT, 0, lambda : None)
m.timer.setTimer( 2)

m.step()
m.step()
m.step()
m.step()
m.step()
