from pcb import PCB
from hardware.cpu_instruction import Program, INT, Instruction
import interrupts
import logging

log= logging.getLogger('os')
END_PROCESS_INTERRUPT= interrupts.interrupt_numbers["syscall_end_process"]

class NoSuchProcess( Exception ):
    pass

class Loader:
    def __init__(self, os):
        log.debug("initializing (program) loader")
        self.os= os
        self.pid_counter=0  #PID of first process is 0

    def _generate_pid(self):
        n= self.pid_counter
        self.pid_counter+=1
        return n

    def load(self, program):
        assert isinstance(program, Program)
        #add "exit()" on program end
        program.instructions.append( Instruction(INT, END_PROCESS_INTERRUPT) )
        pid=  self._generate_pid()
        size= len(program)
        mem= self.os.memory_allocator.allocate( size)
        self.os.machine.ram.writeProgram( mem, program )
        sched_info= self.os.scheduler.new_sched_info()
        pcb= PCB(pid, mem, size, mem+program.start_offset, sched_info)
        #add pcb to system state
        self.os.pcbs[pid]= pcb
        log.debug("loaded program into memory address {mem}. pcb is {pcb}".format(mem=mem, pcb=pcb))
        return pcb

    def unload(self, pid):
        try:
            pcb= self.os.pcbs.pop(pid)  #remove process
        except KeyError:
            raise NoSuchProcess(str(pid))
        program_address= pcb.start_address
        self.os.memory_allocator.free( program_address )
        log.debug("unloaded pcb"+str(pcb))
