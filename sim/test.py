import cpu, timer
import logging
logging.basicConfig(format="%(message)s", level=logging.DEBUG)


c= cpu.Cpu()
t= timer.Timer(c)

process1= cpu.CpuTask('process1', 2)
process2= cpu.CpuTask('process2', 2)

c.add_task( process1 )
t.configure( cpu.CpuTask('interrupt_add_p2', 0, lambda : c.add_task( process2 ) ) , 2)

for i in range(5):
    c.step()
