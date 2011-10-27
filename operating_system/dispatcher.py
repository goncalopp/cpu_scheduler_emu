from scheduler import quantum_attr
import logging
log= logging.getLogger('os')

class NotExecutingAnything( Exception ):
    pass

class AlreadyExecutingSomething( Exception ):
    pass

class Dispatcher:
    def __init__(self, os):
        log.debug("initializing dispatcher")
        self.os= os
        self.currently_executing= None

    def swap_processes(self):
        '''swaps currently executing process for another (per scheduler policy)'''
        log.debug("swapping processes")
        old_pcb= self.currently_executing
        if old_pcb is None:
            raise NotExecutingAnything
        self.os.scheduler.enqueue( old_pcb )
        self.currently_executing= None
        self.start_process()

    def start_process(self):
        '''starts next process (indicated by scheduler)'''
        log.debug("starting next process from scheduler")
        new_pcb= self.os.scheduler.dequeue()
        self.context_switch_to( new_pcb )

    def context_switch_to(self, pcb):
        log.debug("context switching cpu to "+str(pcb))
        if not self.currently_executing is None:
            raise AlreadyExecutingSomething()
        if hasattr(pcb.sched_info, quantum_attr):
            quantum= getattr(pcb.sched_info, quantum_attr)
            log.debug("setting timer to "+str(quantum))
            self.os.timer_driver.unset_timer()  #since we may have not expired the process time slice
            self.os.timer_driver.set_timer( quantum )
        self.currently_executing= pcb
        self.os.machine.cpu.context_switch( pcb.tss )

    def start_program( self, program ):
        '''loads program into new process, adds it to runnable list'''
        pcb= self.os.loader.load( program )
        log.debug("starting program into process: "+str(pcb))
        self.os.scheduler.enqueue( pcb )

    def terminate_process( self, pcb ):
        '''terminates a process'''
        log.debug("terminating process: "+str(pcb))
        if self.os.scheduler.is_running( pcb ):
            self.os.scheduler.remove( pcb )
        self.os.loader.unload( pcb )

    def terminate_current_process( self ):
        log.debug("terminating current process")
        self.terminate_process( self.currently_executing )

    def stop_process(self, pcb):
        '''saves state of process on pcb. does not enqueue it on scheduler'''
        current_state= self.os.machine.cpu.tss
        pcb.tss= current_state
        self.currently_executing=None

    def stop_current_process(self):
        if self.currently_executing is None:
            raise NotExecutingAnything
        self.stop_process( self.currently_executing )

    def get_currently_executing_pcb(self):
        if self.currently_executing is None:
            raise NotExecutingAnything
        return self.currently_executing
