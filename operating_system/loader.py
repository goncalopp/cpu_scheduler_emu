from pcb import PCB
from hardware.cpu_instruction import Program, INT, Instruction
import interrupts
import logging

log= logging.getLogger('os')


class Loader:
    def __init__(self, os):
        log.debug("initializing (program) loader")
        self.os= os
        self.END_PROCESS_INTERRUPT= os.interrupt_handlers.interrupt_numbers["syscall_end_process"]


    def load(self, program):
        assert isinstance(program, Program)
        #add "exit()" on program end
        program.instructions.append( Instruction(INT, self.END_PROCESS_INTERRUPT) )
        mem= self.os.memory_allocator.allocate( len(program) )
        program.writeToRam( self.os.machine.ram, mem )
        log.info("loaded program into memory address "+str(mem))
        return program

    def unload(self, pcb):
        program_address= pcb.start_address
        self.os.memory_allocator.free( program_address )
        log.debug("unloaded pcb"+str(pcb))
