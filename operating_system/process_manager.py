from pcb import PCB
import logging
log= logging.getLogger('os')

class NoSuchProcess( Exception ):
    pass

class ProcessManager:
    def __init__(self, os):
        self.os= os
        self.pcbs={}
        self.pid_counter=0  #PID of first process is 0
        self.changestate_callback=lambda pcb, oldstate, newstate:None

    def _generate_pid(self):
        n= self.pid_counter
        self.pid_counter+=1
        return n

    def get_process(self, pid):
        return self.pcbs[pid]

    def create_process(self, program):
        pid= self._generate_pid()
        sched_info= self.os.scheduler.new_sched_info()
        address= program.get_ram_address()
        pcb= PCB(pid, address, len(program), address+program.start_offset, sched_info, self.changestate_callback)
        self.pcbs[pid]= pcb
        log.debug("created process: "+str(pcb))
        return pcb

    def remove_process(self, pid):
        try:
            pcb= self.pcbs.pop(pid)  #remove process
        except KeyError:
            raise NoSuchProcess(str(pid))

    def get_all_processes(self):
        return self.pcbs.values()

    def set_changestate_callback( f ):
        self.changestate_callback= f
