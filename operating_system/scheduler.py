import logging
log= logging.getLogger('os')

class SchedulingInfo:
    def __init__(self):
        self.user_time = 0
        self.system_time = 0

class RRSchedInfo(SchedulingInfo):
    QUANTUM = 100
    def __init__(self):
        SchedulingInfo.__init__(self)

class Scheduler:
    def __init__(self, os):
        log.debug("initializing scheduler")
        self.os= os

    def enqueue(self, pcb):
        log.debug("scheduler enqueueing process with PID {pid}".format(pid= pcb.pid))
        pass
        
    def dequeue(self):
        log.debug("scheduler dequeueing process")
        pass

    def new_sched_info(self):
        return self.INFO()
    
class RoundRobinScheduler(Scheduler):
    INFO= RRSchedInfo
    def __init__(self, os):
        Scheduler.__init__(self, os)
        self.queue = []
        
    def enqueue(self, pcb):
        Scheduler.enqueue(self)
        self.queue.append(pcb)

    def dequeue(self):
        Scheduler.dequeue(self)
        popped_process = self.queue.pop(0)
        return popped_process
