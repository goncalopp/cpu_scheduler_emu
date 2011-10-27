class PCB:
    '''Process Control Block'''
    
    def __init__(self, pid, start_address, size, sched_info):
        self.pid= pid                       #PID
        self.start_address= start_address   #of program in memory
        self.size= size                     #of program in memory
        self.tss=None                       #cpu context identifier
        self.sched_info=sched_info          #sheduling info

    def __repr__(self):
        return "PCB( PID="+str(self.pid)+" )"

    def renice( n ):
        self.nice=n

