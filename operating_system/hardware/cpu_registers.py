import ram

registers_names= \
[
"PC",   #Program counter
"TSC",  #Timestamp counter
"INT",  #interrupt register
"EAX",  #general purpose
]

class Registers():
    def __init__(self):
        for name in registers_names:
            setattr(self, name, 0)  #all registers at 0 on beggining
        self.PC= ram.OS_MEMORY_START   #except for PC
        self.INT= None

    def __repr__(self):
        content="   ".join([k+":"+str(v) for k,v in vars(self).items()])
        return "<Registers: "+content+">"

    @staticmethod
    def clone( other_registers):
        r= Registers()
        for k,v in vars( other_registers ).items():
            setattr( r, k, v)
        return r
