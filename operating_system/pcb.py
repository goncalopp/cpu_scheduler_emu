from hardware.cpu import TaskStateSegment
import logging
log= logging.getLogger('os')

RUNNING, RUNNABLE, BLOCKED, TERMINATED= range(4)

class PCB:
    '''Process Control Block'''
    
    def __init__(self, pid, start_address, size, pc, sched_info, changestate_callback=lambda pcb, oldstate, newstate:None):
        self.pid= pid                       #PID
        self.start_address= start_address   #of program in memory
        self.size= size                     #of program in memory
        self.tss= TaskStateSegment()        #cpu context identifier
        self.tss.PC= pc                     #address of first instruction
        self.sched_info=sched_info          #sheduling info
        self.changestate_callback= changestate_callback #will be called on state change
        self.state= None
        self.changeState( RUNNABLE, just_started= True )

    def changeState( self, new_state, just_started= False):
        assert new_state in (RUNNING, RUNNABLE, BLOCKED, TERMINATED)
        if new_state == RUNNING:
            assert self.state == RUNNABLE
        if new_state == RUNNABLE:
            assert (self.state in (BLOCKED,RUNNING)) or just_started
        if new_state == BLOCKED:
            assert self.state == RUNNING
        if new_state == TERMINATED:
            assert self.state in (RUNNABLE, BLOCKED)
        self.changestate_callback( self, self.state, new_state)
        self.state= new_state

    def __repr__(self):
        return "PCB "+str(self.pid)
