class Registers():
    def __init__(self):
        self.PC=  128     #program counter
        self.EAX= 0
        self.TSC= 0     #time stamp counter
        self.INT= None  #executing interrupt
    def __repr__(self):
        content="   ".join([k+":"+str(v) for k,v in vars(self).items()])
        return "<Registers: "+content+">"
