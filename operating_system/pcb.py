class PCB:
    '''Process Control Block'''
    
    def __init__(self, pid, start_address, size):
        self.pid= pid                       #PID
        self.start_address= start_address   #of program in memory
        self.size= size                     #of program in memory
        self.nice=0                         #priority
        self.user_time=0                    #total cpu ticks in user mode
        self.system_time=0                  #      "            system mode
        self.last_run= os.get_system_ticks()#last tick the process was run on
    def __repr__(self):
        return "PCB( PID="+self.pid+" )"

    def renice( n ):
        self.nice=n
