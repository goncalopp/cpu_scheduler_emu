from pcb import PCB, RUNNING, RUNNABLE, BLOCKED, TERMINATED
import logging
log= logging.getLogger('os')

class NoSuchProcess( Exception ):
    pass

class ProcessManager:
    def __init__(self, os):
        self.os= os
        self.pcbs={}
        self.pid_counter=0  #PID of first process is 0
        self.changestate_callbacks=[]

    def _generate_pid(self):
        n= self.pid_counter
        self.pid_counter+=1
        return n

    def get_process(self, pid):
        return self.pcbs[pid]

    def start_program( self, program, run=True):
        '''loads program into new process, adds it to runnable list'''
        loaded= self.os.loader.load( program )
        pid= self._generate_pid()
        sched_info= self.os.scheduler.new_sched_info()
        address= loaded.get_ram_address()
        pcb= PCB(pid, address, len(loaded), address+loaded.start_offset, sched_info, self._changestate_callback)
        self.pcbs[pid]= pcb
        pcb.not_started=True
        if run:
            self.run_started_program(pcb)
        else:
            #program will be started later
            pass
        log.debug("created process: "+str(pcb))
        return pcb

    def run_started_program(self, pcb):
        assert isinstance(pcb, PCB)
        assert hasattr(pcb, "not_started")   #program must not already be started
        delattr(pcb, "not_started")
        self.os.scheduler.enqueue( pcb )

    def remove_process(self, pid):
        '''removes a process (terminating it if necessary)'''
        log.debug("removing process: "+str(pid))
        try:
            pcb= self.pcbs.pop(pid)  #remove process
        except KeyError:
            raise NoSuchProcess(str(pid))
        if pcb.state == RUNNABLE:
            self.os.dispatcher.stop_runnable_process( pcb )
        if pcb.state == RUNNING:
            self.os.dispatcher.stop_running_process()
            pcb.changeState( RUNNABLE )
        pcb.changeState( TERMINATED )
        self.os.loader.unload( pcb )

    def get_all_processes(self):
        return self.pcbs.values()

    def add_changestate_callback( self, f ):
        assert callable(f)
        self.changestate_callbacks.append( f )

    def _changestate_callback( self, pcb, oldstate, newstate ):
        '''function that handles a pcb changestate'''
        for f in self.changestate_callbacks:
            f( pcb, oldstate, newstate )
