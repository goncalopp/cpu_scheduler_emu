from pcb import RUNNING, RUNNABLE, BLOCKED
import logging
log= logging.getLogger('os')

class NoMoreRunnableProcesses( Exception ):
    '''no more processes are runnable atm'''
    pass

class SchedulingInfo:
    def __init__(self):
        self.user_time = 0
        self.system_time = 0
        self.last_run_on= 0

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
        self.os.process_manager.add_changestate_callback( self.scheduler_changestate )  #register for pcb state change


    def enqueue(self, pcb):
        log.debug("scheduler enqueueing process with PID {pid}".format(pid= pcb.pid))
        pcb.last_enqueue= self.os.get_system_ticks()
        pass
        
    def dequeue(self):
        log.debug("scheduler dequeueing process")
        pass

    def scheduler_changestate(self, pcb, oldstate, newstate):
        if newstate==RUNNING:
            #was put running
            pcb.sched_info.last_run_on= self.os.get_system_ticks()
            log.info("pcb "+str(pcb)+" is now running ("+str(pcb.sched_info.last_run_on))
        if oldstate==RUNNING and (newstate==RUNNABLE or newstate==BLOCKED):
            #was stopped
            current_time= self.os.get_system_ticks()
            elapsed= current_time - pcb.sched_info.last_run_on
            log.info("pcb "+str(pcb)+" stopped. runned for ("+str(elapsed))
            pcb.sched_info.user_time+= elapsed


    def new_sched_info(self):
        return self.INFO()

    def remove(self, pcb):
        '''removes pcb from runnable queue'''
        pass

class TimeSliceScheduler(Scheduler):
    def __init__(self, os):
        Scheduler.__init__(self,os)
        self.os.process_manager.add_changestate_callback( self.timeslice_changestate )  #register for pcb state change

    def timeslice_changestate(self, pcb, oldstate, newstate):
        if oldstate==RUNNABLE and newstate==RUNNING:
            #a process was put running. set timer for timeslice
            quantum= pcb.sched_info.quantum
            log.debug("setting timer to "+str(quantum))
            self.os.timer_driver.unset_timer()  #since we may have not expired the process time slice
            self.os.timer_driver.set_timer( max(1,int(quantum)) )   #minimum timeslice is 1

class SignalledScheduler(TimeSliceScheduler):
    def __init__(self, os):
        TimeSliceScheduler.__init__(self, os)
        self.os.process_manager.add_changestate_callback( self.signaled_changestate )  #register for pcb state change

    def signaled_changestate(self, pcb, oldstate, newstate):
        if oldstate==RUNNING and newstate==RUNNABLE:
            if self.os.get_system_ticks() - pcb.sched_info.last_run_on >= pcb.sched_info.quantum:
                log.debug("detected timeslice end on pcb "+str(pcb))
                self._signal_time_slice_end( pcb )
        if oldstate==RUNNING and newstate==BLOCKED:
            log.debug("detected I/O block on pcb "+str(pcb))
            self._signal_io_block(pcb)
        
    def _signal_time_slice_end(self, pcb):
        '''signals process pcb finished its time slice'''
        log.debug("process{pid} finished its time slice".format(pid=pcb.pid))
        pass

    def _signal_io_block(self, pcb):
        ''' signals process pcb blocked for an IO operation '''
        log.debug("process{pid} blocked for IO".format(pid=pcb.pid))
        pass

class RoundRobinScheduler(TimeSliceScheduler):
    INFO= TimeSliceSchedInfo
    def __init__(self, os):
        TimeSliceScheduler.__init__(self, os)
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
        SignalledScheduler.__init__(self, os)
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
                pcb= l.pop(0)
                return pcb
        self.active, self.expired = self.expired, self.active
        for l in self.active:
            if len(l) > 0:
                pcb= l.pop(0)
                return pcb
        raise NoMoreRunnableProcesses()

    def _signal_io_block(self, pcb):
        SignalledScheduler._signal_io_block(self, pcb)
        pcb_priority =  pcb.sched_info.priority
        pcb.sched_info.times_ran +=1
        if pcb_priority < self.PRIORITY_LVLS:
            pcb_priority +=1
            pcb.sched_info.quantum = pcb.sched_info.quantum * 0.90

    def _signal_time_slice_end(self, pcb):
        SignalledScheduler._signal_time_slice_end(self, pcb)
        pcb_priority = pcb.sched_info.priority
        pcb.sched_info.times_ran += 1
        if pcb_priority > 0:
            pcb_priority -= 1
            pcb.sched_info.quantum = pcb.sched_info.quantum * 1/0.90
