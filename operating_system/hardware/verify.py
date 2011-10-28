import verification_programs
import ram, cpu
from machine import Machine


#import pdb; pdb.set_trace()
for test in verification_programs.tests:
    my_pc= Machine()
    program= test.program
    address= ram.PROGRAM_MEMORY_START
    for i in xrange(0, len(program)):
        program.writeToRam( my_pc.ram,  address)
    my_pc.cpu.registers.PC= address + program.start_offset
    while my_pc.cpu.registers.PC<address+len(program):
        try:
            my_pc.step()
        except cpu.Poweroff:
            break
    test.verify( my_pc.ram, address )
    print "test '"+test.name+"' passed!"
