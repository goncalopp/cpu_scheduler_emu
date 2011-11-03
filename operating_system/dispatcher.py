from hardware.cpu_instruction import programFromString
from pcb import RUNNING, RUNNABLE, BLOCKED
import scheduler
import logging
log= logging.getLogger('os')

class NoMoreProcesses( Exception ):
    pass

class AlreadyExecutingSomething( Exception ):
    pass
    
class NotExecutingAnything( Exception ):
    pass

class Dispatcher:
    def __init__(self, os):
        log.debug("initializing dispatcher")
        self.os= os
        self.currently_executing= None
        self.idle_process= self.os.process_manager.start_program( programFromString("NOOP\nJMP\t-1"))

    def timer_end(self):
        self.swap_processes()

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
        n_processes= len(self.os.process_manager.get_all_processes())
        if n_processes<2:
            assert n_processes==1 #must have idle process
            raise NoMoreProcesses("All processes have finished")
        new_pcb= self.os.scheduler.dequeue()
        assert new_pcb.state== RUNNABLE
        if new_pcb==self.idle_process:              #if next runnable is the idle process
            try:
                new_pcb= self.os.scheduler.dequeue()    #are there any other runnable?
                self.os.scheduler.enqueue( self.idle_process )  #yes, great, do that one instead
            except scheduler.NoMoreRunnableProcesses:
                pass                                    #only idle process is runnable...
        self.context_switch_to( new_pcb )

    def context_switch_to(self, pcb):
        log.debug("context switching cpu to "+str(pcb))
        if not self.currently_executing is None:
            raise AlreadyExecutingSomething()
        if pcb == self.idle_process:
            self.os.timer_driver.unset_timer()
            self.os.timer_driver.set_timer( 1 ) #run idle process as little as possible
        self.currently_executing= pcb
        pcb.changeState( RUNNING )
        self.os.machine.cpu.context_switch( pcb.tss )

    def stop_running_process(self):
        '''saves state of process on pcb, does not enqueue it on scheduler'''
        log.debug("stopping running process")
        if self.currently_executing is None:
            raise NotExecutingAnything
        pcb= self.currently_executing
        assert pcb.state==RUNNING
        pcb.tss= self.os.machine.cpu.tss
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
