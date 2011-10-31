from itertools import chain
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

class TimeSliceSchedInfo(SchedulingInfo):
    DEF_QUANTUM = 100
    def __init__(self):
        SchedulingInfo.__init__(self)
        self.quantum= self.DEF_QUANTUM

class OOneSchedInfo(TimeSliceSchedInfo):
    def __init__(self):
        TimeSliceSchedInfo.__init__(self)
        self.priority = 0
        self.priotity_class = 0
        self.times_ran = 0

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

class TimeSliceScheduler(Scheduler):
    def __init__(self, os):
        Scheduler.__init__(self,os)

class SignalledScheduler(TimeSliceScheduler):
    def __init__(self, os):
        TimeSliceScheduler.__init__(self, os)
        
    def signal_time_slice_end(self, pcb):
        '''signals process pcb finished its time slice'''
        log.debug("process{pid} finished its time slice".format(pid=pcb.pid))
        pass

    def signal_io_block(self, pcb):
        ''' signals process pcb blocked for an IO operation '''
        log.debug("process{pid} blocked for IO".format(pid=pcb.pid))
        pass

class RoundRobinScheduler(TimeSliceScheduler):
    INFO= TimeSliceSchedInfo
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

class OOneScheduler(SignalledScheduler):
    INFO= OOneSchedInfo
    PRIORITY_LVLS = 4
    def __init__(self, os):
        Scheduler.__init__(self, os)
        self.interactive_threshold = (int) (self.PRIORITY_LVLS/2)
        self.active = [[]]*self.PRIORITY_LVLS
        self.expired = [[]]*self.PRIORITY_LVLS

    def enqueue(self, pcb):
        Scheduler.enqueue(self, pcb)
        pcb_priority = pcb.sched_info.priority  #check the process priority
        if pcb.sched_info.times_ran < 2 and pcb_priority >= self.interactive_threshold:
            self.active[pcb_priority].append(pcb)
        else:
            self.expired[pcb_priority].append(pcb)

    def dequeue(self):
        Scheduler.dequeue(self)
        for l in self.active:
            if len(l) > 0:
                return l.pop(0)
        self.active, self.expired = self.expired, self.active
        for l in self.active:
            if len(l) > 0:
                return l.pop(0)
        raise NoMoreRunnableProcesses()

    def signal_io_block(self, pcb):
        pcb_priority =  pcb.sched_info.priority
        pcb.sched_info.times_ran +=1
        if pcb_priority < self.PRIORITY_LVLS:
            pcb_priority +=1
            pcb.sched_info.quantum = pcb.sched_info.quantum * 0.90

    def signal_time_slice_end(self, pcb):
        pcb_priority = pcb.sched_info.priority
        pcb.sched_info.times_ran += 1
        if pcb_priority > 0:
            pcb_priority -= 1
            pcb.sched_info.quantum = pcb.sched_info.quantum * 1/0.90
