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
        if not self.currently_executing is None:
            raise AlreadyExecutingSomething()
        self.currently_executing= pcb
        log.debug("context switching cpu to "+str(pcb))
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
