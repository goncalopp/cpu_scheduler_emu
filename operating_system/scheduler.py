from pcb import RUNNING, RUNNABLE, BLOCKED, CREATED, TERMINATED
states_dict= {RUNNING:"Running   ", RUNNABLE:"Runnable  ", BLOCKED:"Blocked   ", TERMINATED:"Terminated"}
import logging
log= logging.getLogger('os')

class NoMoreRunnableProcesses( Exception ):
    '''no more processes are runnable atm'''
    pass
    
class PCBNotInScheduler( Exception ):
    '''Process is not in the scheduler '''
    pass

class SchedulingInfo:
    def __init__(self):
        pass

class TimeSliceSchedInfo(SchedulingInfo):
    DEF_QUANTUM = 100
    MINIMUM_QUANTUM= 1
    def __init__(self):
        SchedulingInfo.__init__(self)
        self.quantum= self.DEF_QUANTUM

class OOneSchedInfo(TimeSliceSchedInfo):
    def __init__(self):
        TimeSliceSchedInfo.__init__(self)
        self.priority = 0
        self.times_ran = 0

class StrideSchedInfo(TimeSliceSchedInfo):
    DEF_BRIBE = 1.0
    def __init__(self):
        TimeSliceSchedInfo.__init__(self)
        self.bribe = self.DEF_BRIBE
        self.meter_rate = 0
        self.metered_time = 0

class Scheduler:
    def __init__(self, os):
        log.debug("initializing scheduler")
        self.os= os

    def enqueue(self, pcb):
        log.debug("scheduler enqueueing process with PID {pid}".format(pid= pcb.pid))
        pcb.last_enqueue= self.os.get_system_ticks()
        pass
        
    def dequeue(self):
        log.debug("scheduler dequeueing process")
        pass


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
            quantum= max(TimeSliceSchedInfo.MINIMUM_QUANTUM,int(quantum))   #quantum must be integer, with a minimum
            log.debug("setting timer to "+str(quantum))
            self.os.timer_driver.unset_timer()  #since we may have not expired the process time slice
            self.os.timer_driver.set_timer( quantum )

class SignalledScheduler(TimeSliceScheduler):
    def __init__(self, os):
        TimeSliceScheduler.__init__(self, os)
        self.os.process_manager.add_changestate_callback( self.signaled_changestate )  #register for pcb state change

    def signaled_changestate(self, pcb, oldstate, newstate):
        if oldstate==RUNNING and newstate==RUNNABLE:
            if self.os.machine.timer.time==0:
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
        self.os.process_manager.add_changestate_callback( self.oone_changestate )
        self.interactive_threshold = (int) (self.PRIORITY_LVLS/2)
        self.active = [ [] for x in range(self.PRIORITY_LVLS)]
        self.expired = [ [] for x in range(self.PRIORITY_LVLS)]

    def enqueue(self, pcb):
        SignalledScheduler.enqueue(self, pcb)
        pcb_priority = pcb.sched_info.priority  #check the process priority
        if pcb.sched_info.times_ran < 2 and pcb_priority >= self.interactive_threshold:
            self.active[pcb_priority].append(pcb)
        else:
            self.expired[pcb_priority].append(pcb)
            pcb.sched_info.times_ran=0

    def dequeue(self):
        SignalledScheduler.dequeue(self)
        def dequeue_from_active():
            for l in reversed(self.active):
                try:
                    pcb= l.pop(0)
                    return pcb
                except IndexError:
                    pass
            raise NoMoreRunnableProcesses()
        try:
            return dequeue_from_active()
        except NoMoreRunnableProcesses:
            self.active, self.expired = self.expired, self.active
            return dequeue_from_active()

    def oone_changestate(self, pcb, oldstate, newstate):
        if newstate==RUNNING:
            pcb.sched_info.times_ran+=1

    def _signal_io_block(self, pcb):
        SignalledScheduler._signal_io_block(self, pcb)
        if pcb.sched_info.priority < self.PRIORITY_LVLS-1:
            pcb.sched_info.priority+= 1
            pcb.sched_info.quantum *= 0.9

    def _signal_time_slice_end(self, pcb):
        SignalledScheduler._signal_time_slice_end(self, pcb)
        if pcb.sched_info.priority > 0:
            pcb.sched_info.priority -= 1
            pcb.sched_info.quantum *= (1/0.9)

    def remove(self, pcb):
        found = 0
        for l in self.active:
            if pcb in l:
                l.remove(pcb)
                found = 1
                break
        if not found:
            for l in self.expired:
                if pcb in l:
                    l.remove(pcb)
                    found = 1
                    break
            if not found:
                PCBNotInScheduler()

class StrideScheduler(SignalledScheduler):
    INFO= StrideSchedInfo
    def __init__(self, os):
        SignalledScheduler.__init__(self, os)
        self.runqueue = []
        self.total_tickets = 0      #total number of bribery tickets
        self.ficticious_meter = 0   #ficticious meter for dynamic process initialization
        self.os.process_manager.add_changestate_callback( self.stride_changestate )

    def stride_changestate(self, pcb, oldstate, newstate):
        if oldstate==CREATED:               #initialize shed_info meters
            pcb.sched_info.meter_rate = (1.0/pcb.sched_info.bribe)
            pcb.sched_info.metered_time = self.ficticious_meter + pcb.sched_info.meter_rate
            self.total_tickets += pcb.sched_info.bribe
        if oldstate==RUNNING and newstate==RUNNABLE:        #process finished it's timeslice
            pcb.sched_info.metered_time += pcb.sched_info.meter_rate    #updates metered_time
            bribe = pcb.sched_info.bribe
            if bribe > 1:                                   #minimum bribe
                pcb.sched_info.bribe -= 1
                self.total_tickets -= 1                
            pcb.sched_info.meter_rate = 1.0/pcb.sched_info.bribe
        if oldstate==RUNNING and newstate==BLOCKED:
            pcb.sched_info.bribe += 1
            pcb.sched_info.meter_rate = 1.0/pcb.sched_info.bribe
            self.total_tickets += 1
            pcb.sched_info.remaining_time = pcb.sched_info.metered_time - self.ficticious_meter
        if oldstate==BLOCKED and newstate==RUNNABLE:
            pcb.sched_info.metered_time = self.ficticious_meter + pcb.sched_info.remaining_time
        if oldstate==TERMINATED:
            self.total_tickets -= pcb.sched_info.bribe
        if oldstate==RUNNING:
            self.ficticious_meter += 1.0/self.total_tickets   #update ficticious meter
            #print "CLOCK = " + str(self.os.get_system_ticks()) + ", FICT METER = " + str(self.ficticious_meter*pcb.sched_info.quantum)+ ", PID = " + str(pcb.pid) + ", NEWSTATE = " + str(states_dict[newstate]) + ", METERED_TIME = " + str(pcb.sched_info.metered_time*pcb.sched_info.quantum) + ", BRIBE = " + str(pcb.sched_info.bribe)

    def enqueue(self, pcb):
        Scheduler.enqueue(self, pcb)        
        self.runqueue.append(pcb)
        self.runqueue.sort(key= lambda pcb: pcb.sched_info.metered_time)   #sort runqueue by ascending meters

    def dequeue(self):
        Scheduler.dequeue(self)
        if len(self.runqueue) > 0:
            pcb = self.runqueue.pop(0)
            return pcb
        else:
            raise NoMoreRunnableProcesses()

    def remove(self, pcb):
        self.runqueue.remove(pcb)

    def _signal_io_block(self, pcb):
        SignalledScheduler._signal_io_block(self, pcb)

    def _signal_time_slice_end(self, pcb):
        SignalledScheduler._signal_time_slice_end(self, pcb)
