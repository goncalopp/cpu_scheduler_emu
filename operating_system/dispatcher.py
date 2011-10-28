from hardware.cpu_instruction import programFromString
import scheduler
import logging
log= logging.getLogger('os')

class NotExecutingAnything( Exception ):
    pass

class AlreadyExecutingSomething( Exception ):
    pass

class NoMoreProcesses( Exception ):
    pass

class Dispatcher:
    def __init__(self, os):
        log.debug("initializing dispatcher")
        self.os= os
        self.currently_executing= None
        self.idle_process= self.start_program( programFromString("NOOP\nJMP\t-1"))

    def swap_processes(self):
        '''swaps currently executing process for another (per scheduler policy)'''
        log.debug("swapping processes")
        old_pcb= self.currently_executing
        self.stop_current_process()
        self.os.scheduler.enqueue( old_pcb )
        self.start_process()

    def start_process(self):
        '''starts next process (indicated by scheduler)'''
        log.debug("starting next process from scheduler")
        if len(self.os.pcbs)<2:
            assert len(self.os.pcbs)==1 #must have idle process
            raise NoMoreProcesses("All processes have finished")
        new_pcb= self.os.scheduler.dequeue()
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
        else:
            if hasattr(pcb.sched_info, scheduler.quantum_attr):
                #scheduler supports preemption , using timer regulated time slices
                quantum= getattr(pcb.sched_info, scheduler.quantum_attr)
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
        return pcb

    def terminate_process( self, pcb ):
        '''terminates a process'''
        log.debug("terminating process: "+str(pcb))
        if self.os.scheduler.is_runnable( pcb ):
            self.os.scheduler.remove( pcb )
        self.os.loader.unload( pcb.pid )
        self.start_process()

    def stop_and_terminate_current_process( self ):
        log.debug("stopping and terminating current process")
        pcb= self.currently_executing
        self.stop_current_process()
        self.terminate_process( pcb )

    def stop_current_process(self):
        '''saves state of process on pcb. does not enqueue it on scheduler'''
        if self.currently_executing is None:
            raise NotExecutingAnything
        pcb= self.currently_executing
        current_state= self.os.machine.cpu.tss
        pcb.tss= current_state
        self.currently_executing=None

    def get_currently_executing_pcb(self):
        if self.currently_executing is None:
            raise NotExecutingAnything
        return self.currently_executing
