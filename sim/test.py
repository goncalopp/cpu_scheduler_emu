import machine
import cpu
import logging
logging.basicConfig(format="%(message)s", level=logging.DEBUG)


m= machine.Machine()

process1= cpu.TaskClass('process1', 2)
process2= cpu.TaskClass('process2', 2)

m.cpu.add_task( process1 )
m.set_interrupt( machine.TIMER_INTERRUPT, 0, lambda : m.cpu.add_task(process2))
m.timer.configure( 2)

for i in range(5):
    m.step()
print m.cpu.tsc
