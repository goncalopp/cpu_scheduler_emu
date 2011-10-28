from hardware import verification_programs, cpu
from hardware.machine import Machine
from kernel import Kernel
import dispatcher

MAX_CYCLES= 10000000

my_pc= Machine()
my_os= Kernel( my_pc )
for test in verification_programs.tests:
    pcb= my_os.dispatcher.start_program( test.program )
    test.tmp_var_start_address= pcb.start_address
my_os.kickstart()

for cycle in xrange(MAX_CYCLES):
        try:
            my_pc.step()
        except cpu.Poweroff:
            break
        except dispatcher.NoMoreProcesses:
            break

for test in verification_programs.tests:
    address= test.tmp_var_start_address
    test.verify( my_pc.ram, address )
    print "test '"+test.name+"' passed!"
