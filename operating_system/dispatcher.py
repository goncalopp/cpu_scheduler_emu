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
        old_pcb= self.currently_executing
        if old_pcb is None:
            raise NotExecutingAnything

        self.os.scheduler.enqueue( old_pcb )
        new_pcb= self.os.scheduler.dequeue()
        log.debug("swapped processes. old: "+str(old_pcb)+", new: "+str(new_pcb))
        self.currently_executing= None
        self.context_switch( new_pcb )

    def context_switch_to(self, pcb):
        if not self.currently_executing is None:
            raise AlreadyExecutingSomething()
        log.debug("context switching cpu to "+str(pcb))
        self.os.cpu.context_switch( pcb.tss )
