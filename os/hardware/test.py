import machine
import cpu

m= machine.Machine( 100 )

m.set_interrupt_handler( machine.TIMER_INTERRUPT, 0, lambda : None)
m.timer.setTimer( 2)

while True:
    try:
        m.step()
    except cpu.Poweroff:
        print "Execution ended"
        break
