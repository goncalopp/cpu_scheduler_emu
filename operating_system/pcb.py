from hardware.cpu import TaskStateSegment


class PCB:
    '''Process Control Block'''
    
    def __init__(self, pid, start_address, size, pc, sched_info):
        self.pid= pid                       #PID
        self.start_address= start_address   #of program in memory
        self.size= size                     #of program in memory
        self.tss= TaskStateSegment()        #cpu context identifier
        self.tss.PC= pc                     #address of first instruction
        self.sched_info=sched_info          #sheduling info

    def __repr__(self):
        return "PCB "+str(self.pid)
