import logging
log= logging.getLogger('os')

class Scheduler:
    def __init__(self, os):
        log.debug("initializing scheduler")
        self.os= os

    def currently_executing_pcb(self):
        #TODO
        pass

    def schedule(self):
        log.debug("executing scheduler")
        #TODO
        pass

    def end_process_interrupt_handler(self):
        log.debug("process end was signaled")
        #TODO
        pass
