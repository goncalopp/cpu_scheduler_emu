import logging
log= logging.getLogger('os')

class NoMoreRunnableProcesses( Exception ):
    '''no more processes are runnable atm'''
    pass

quantum_attr= "quantum"

class SchedulingInfo:
    def __init__(self):
        self.user_time = 0
        self.system_time = 0

class RRSchedInfo(SchedulingInfo):
    QUANTUM = 100
    def __init__(self):
        SchedulingInfo.__init__(self)
        self.quantum= self.QUANTUM

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

    def is_runnable(self, pcb):
        '''checks if a pcb is runnable'''
        pass

    def remove(self, pcb):
        '''removes pcb from runnable queue'''
        pass
    
class RoundRobinScheduler(Scheduler):
    INFO= RRSchedInfo
    def __init__(self, os):
        Scheduler.__init__(self, os)
        self.queue = []
        
    def enqueue(self, pcb):
        Scheduler.enqueue(self, pcb)
        self.queue.append(pcb)

    def dequeue(self):
        Scheduler.dequeue(self)
        try:
            popped_process = self.queue.pop(0)
        except IndexError:
            raise NoMoreRunnableProcesses()
        return popped_process

    def is_runnable(self, pcb):
        return pcb in self.queue

    def remove(self, pcb):
        self.queue.remove(pcb)
