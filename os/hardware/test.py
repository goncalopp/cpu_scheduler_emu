import machine
import cpu

m= machine.Machine( 100 )

process1= cpu.TaskClass('process1', 2)
process2= cpu.TaskClass('process2', 2)

m.cpu.add_task( process1 )
m.set_interrupt_handler( machine.TIMER_INTERRUPT, 0, lambda : m.cpu.add_task(process2))
m.timer.setTimer( 2)

while True:
    try:
        m.step()
    except cpu.NoTask:
        break
