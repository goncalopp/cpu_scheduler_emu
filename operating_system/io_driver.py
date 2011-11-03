import scheduler
import logging
from pcb import RUNNABLE, BLOCKED
log= logging.getLogger('os')

class IODriver:
    def __init__(self, os):
        log.debug("initializing IO Driver")
        self.os= os
        self.pcb_queue=[]   #processes waiting for I/O request generation
        self.waiting= False #waiting for response to I/O request?

    def request_io(self):
        '''syscall, available for processes to request i/o'''
        pcb= self.os.dispatcher.get_currently_executing_pcb()  #pcb which made request (the one currently executing)
        log.debug("got io request from pcb "+str(pcb))
        self.pcb_queue.append( pcb )
        if not self.waiting:
            self._request_io_to_device()
        self.os.dispatcher.stop_running_process()   #current process is now blocked (not added to scheduler)
        pcb.changeState( BLOCKED )
        self.os.dispatcher.start_next_process()  #start next process
        
    def io_interrupt_handler(self):
        '''called when I/O device has replied to last request'''
        log.debug("handling io interrupt")
        pcb= self.pcb_queue.pop(0)      #pcb which made io request
        pcb.changeState( RUNNABLE )
        self.os.scheduler.enqueue( pcb) # is now ready to start again
        self.waiting=False
        if len(self.pcb_queue)>0:
            #process next io request
            self._request_io_to_device()
            
    def _request_io_to_device(self):
        log.debug("making io request to device")
        assert self.waiting==False
        assert len(self.pcb_queue)>=1
        self.waiting= True
        self.os.machine.io.io_request()
