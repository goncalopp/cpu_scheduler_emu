from operating_system.pcb import RUNNING, RUNNABLE, BLOCKED, TERMINATED
states_dict= {RUNNING:"Running   ", RUNNABLE:"Runnable  ", BLOCKED:"Blocked   ", TERMINATED:"Terminated"}

import logging
trace_log= logging.getLogger('process_trace')
formatter = logging.Formatter('%(asctime)s\t%(message)s')
hdlr = logging.FileHandler('process_trace.log.tsv', mode="w")
hdlr.setFormatter(formatter)
trace_log.addHandler(hdlr)
trace_log.setLevel(logging.DEBUG)



class StateChange:
    def __init__(self, clock, pid, newstate):
        assert newstate in states_dict.keys()
        self.clock, self.pid, self.state= clock, pid, newstate
    def __repr__(self):
        return "\t".join([str(self.clock), str(self.pid),states_dict[self.state]])
        
class ProcessInfo:
    def __init__(self, program_duration, pid):
        self.pid= pid
        self._program_duration= program_duration
        self.waiting_time= 0
        self.blocked_times= 0
        self.start_clock= -1
        self.termination_clock= -1
        self.executed_clocks= 0
    def turnaround(self):
        assert 0 <= self.start_clock <= self.termination_clock
        return self.termination_clock-self.start_clock
    def terminated(self):
        return self.termination_clock>=0



class ProcessTracer:
    def __init__(self, os):
        self.os= os
        os.process_manager.add_changestate_callback( self.process_changestate_callback )
        self.trace=[]
        self.processed= False

    def process_changestate_callback(self, pcb, oldstate, newstate):
        assert not self.processed
        clock= self.os.get_system_ticks()
        self.trace.append( StateChange(clock, pcb.pid, newstate) )

    def process( self, pids_durations ):
        assert not self.processed
        all_pids= set([cs.pid for cs in self.trace])
        pids_durations[0]= float("inf") #duration of idle process is infinite...
        tmp=all_pids.difference(set(pids_durations.keys()))
        assert len(tmp)==0 or (len(tmp)==1 and 0 in tmp)    #function was given the duration of all processes
        last_states= {}
        self.trace.insert(0,StateChange(0, 0, RUNNABLE))  #workaround, since we don't receive this notification (process statechange event generated before callbacks are installed)
        i=0
        while i<len(self.trace)-1:      #remove repeated idle process execution and stopping
            s1,s2= self.trace[i], self.trace[i+1]
            if s1.pid==s2.pid==0 and s1.state==RUNNABLE and s2.state==RUNNING:
                assert s1.clock==s2.clock                               #idle process was stopped and started immediatelly
                self.trace.pop(i)
                self.trace.pop(i)   #was i+1
                i-=2
            i+=1

        for s in self.trace:
            pid= s.pid
            try:
                last_state= last_states[pid]
            except KeyError:
                assert s.state==RUNNABLE
                last_states[pid]= s
                s.clocks_done= 0
                s.clocks_left= pids_durations[ pid ]
                continue
            assert pid == last_state.pid
            s.clocks_left= last_state.clocks_left
            s.clocks_done= last_state.clocks_done
            if last_state.state==RUNNING:
                #stopped running
                runned_for= s.clock-last_state.clock
                s.clocks_done+= runned_for
                s.clocks_left-= runned_for
            last_states[pid]= s
        self.processed=True

    def calculate_general_statistics(self, io_operation_duration, programs_durations, trace):
        assert self.processed
        process_info= {}
        last_states= {}
        for s in self.trace:
            pid= s.pid
            try:
                last_state= last_states[pid]
            except KeyError:
                assert s.state==RUNNABLE
                last_states[pid]= s
                info= process_info[pid]= ProcessInfo( programs_durations[pid], pid )
                info.start_clock= s.clock
                continue
            assert pid == last_state.pid
            info = process_info[pid]
            if last_state.state==RUNNING and s.state==BLOCKED:
                #stopped running
                clocks_executed= s.clock-last_state.clock
                info.executed_clocks+= s.clock-last_state.clock
                info.blocked_times+=1
            if last_state.state==RUNNING and s.state==RUNNABLE:
                info.executed_clocks+= s.clock-last_state.clock
            if last_state.state==RUNNABLE and s.state==RUNNING:
                info.waiting_time+= s.clock-last_state.clock
            if s.state==TERMINATED:
                if s.clocks_left==0:
                    info.terminated_clock= s.clock
            assert info.executed_clocks==s.clocks_done
            last_states[pid]= s
        total_time=trace[-1].clock
        cpu_busy_clocks= sum(map(lambda i: i.executed_clocks, [i for i in process_info.values() if i.pid!=0]))
        total_io_operations= sum(map(lambda i: i.blocked_times, process_info.values()))
        io_busy_clocks= io_operation_duration*total_io_operations
        import pdb; pdb.set_trace()
        return (total_time, cpu_busy_clocks, io_busy_clocks)
    def get_pid_trace(self, pid):
        states= filter( lambda sc: sc.pid==pid, self.trace)

    def get_trace(self):
        return self.trace
    
    def __repr__(self):
        assert self.processed
        return "\n".join( [ "\t".join(map(str, [state, state.clocks_done, state.clocks_left])) for state in self.trace])
