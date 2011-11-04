from pcb import RUNNING, RUNNABLE, BLOCKED
from idle_process import IdleProcessScheduler
import logging
log= logging.getLogger('os')

class NoMoreProcesses( Exception ):
    pass

class AlreadyExecutingSomething( Exception ):
    pass
    
class NotExecutingAnything( Exception ):
    pass

class MultipleContextSwithInSameClock( Exception ):
    pass

class Dispatcher:
    def __init__(self, os):
        log.debug("initializing dispatcher")
        self.os= os
        self.currently_executing= self.last_executing= None
        self.last_switch_clock=-1

    def swap_processes(self):
        '''swaps currently executing process for another (per scheduler policy)'''
        log.debug("swapping processes")
        pcb= self.stop_running_process()
        pcb.changeState( RUNNABLE )
        self.os.scheduler.enqueue( pcb )
        self.start_next_process()

    def start_next_process(self):
        '''starts next process (indicated by scheduler)'''
        log.debug("starting next process from scheduler")
        current_clock= self.os.get_system_ticks()
        if self.last_switch_clock==current_clock:
            raise MultipleContextSwithInSameClock()
        self.last_switch_clock= current_clock
        n_processes= len(self.os.process_manager.get_all_processes())
        if n_processes==0 or ( n_processes==1 and isinstance(self.os.scheduler, IdleProcessScheduler)):
            raise NoMoreProcesses("All processes have finished")
        new_pcb= self.os.scheduler.dequeue()
        self._context_switch_to( new_pcb )

    def _context_switch_to(self, pcb):
        log.info("context switching cpu to "+str(pcb))
        if not self.currently_executing is None:
            raise AlreadyExecutingSomething()
        self.currently_executing= pcb
        pcb.changeState( RUNNING )
        self.os.machine.cpu.context_switch( pcb.tss )

    def stop_running_process(self):
        '''saves state of process on pcb, does not enqueue it on scheduler, doesn't change pcb state'''
        if self.currently_executing is None:
            raise NotExecutingAnything
        pcb= self.currently_executing
        assert pcb.state==RUNNING
        pcb.tss= self.os.machine.cpu.tss
        log.info("stopping running process. saved tss "+str(pcb.tss))
        self.last_executing= pcb
        self.currently_executing=None
        return pcb

    def stop_runnable_process( self, pcb ):
        log.debug("stop runnable process: "+str(pcb))
        assert pcb.state == RUNNABLE
        self.os.scheduler.remove( pcb )

    def get_currently_executing_pcb(self):
        if self.currently_executing is None:
            raise NotExecutingAnything
        return self.currently_executing

    def remove_current_process(self):
        self.os.process_manager.remove_process( self.currently_executing.pid )
        self.start_next_process()
