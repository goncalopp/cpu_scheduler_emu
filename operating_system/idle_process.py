from hardware.cpu_instruction import programFromString
import scheduler
import logging
log= logging.getLogger('os')


IDLE_PROCESS_CODE= '''
NOOP
JMP $0
'''

class IdleProcessScheduler:
    def __init__(self, os):
        log.debug("Installing idle process (scheduler wrapper)")
        self.os= os
        assert isinstance(os.scheduler, scheduler.TimeSliceScheduler)   #OS scheduler must support time slices for idle process to work...
        self.wrapped_scheduler= os.scheduler    #save kernel scheduler
        os.scheduler= self                      #substitute it by wrapper
        for f_name in ("new_sched_info", "remove"):
            #wrap untouched functions
            setattr(self, f_name, getattr(self.wrapped_scheduler, f_name))
        self.busy= True #must be true since process_manager.start_program enqueues it
        self.idle_process= self.os.process_manager.start_program( programFromString(IDLE_PROCESS_CODE), run=False)
        self.idle_process.sched_info.quantum= 1 #idle_process must run
        self.os.process_manager.run_started_program( self.idle_process )

    def dequeue(self):
        try:
            return self.wrapped_scheduler.dequeue() 
        except scheduler.NoMoreRunnableProcesses:
            assert self.busy==False
            self.busy=True
            return self.idle_process            #only idle process is runnable...

    def enqueue(self, pcb):
        if pcb==self.idle_process:
            assert self.busy==True
            self.busy= False
        else:
            self.wrapped_scheduler.enqueue(pcb)
