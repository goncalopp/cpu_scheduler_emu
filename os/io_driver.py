class IODriver:
    def __init__(self, os):
        self.os= os
        self.pcb_queue=[]
        self.waiting= False

    
    def request_io(self):
        pcb= self.os.currently_executing_pcb()  #pcb which made request (the one currently executing)
        self.pcb_queue.append( pcb )
        if not self.waiting:
            self._request_io_to_device()
        
    def io_interrupt_handler(self):
        pcb= self.pcb_queue.pop(0) #pcb which made io request
        #TODO: wake up (unblock) pcb
        if len(self.pcb_queue)==0:
            #no more io requests
            self.waiting=False
        else:
            #process next io requ89est
            self._request_io_to_device()
            
    def _request_io_to_device(self):
        assert self.waiting==False
        assert len(self.pcb_queue)>=1
        #TODO: block pcb
        self.os.machine.io_device.io_request()
        
            
