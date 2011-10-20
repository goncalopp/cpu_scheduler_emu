import machine
import cpu
import logging
logging.basicConfig(format="%(message)s", level=logging.DEBUG)


m= machine.Machine( 100 )

process1= cpu.TaskClass('process1', 2)
process2= cpu.TaskClass('process2', 2)

m.cpu.add_task( process1 )
m.set_interrupt_handler( machine.TIMER_INTERRUPT, 0, lambda : m.cpu.add_task(process2))
m.timer.setTimer( 2)

for i in range(5):
    m.step()
print m.cpu.tsc
