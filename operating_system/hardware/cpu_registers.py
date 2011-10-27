import ram

registers_names= \
[
"PC",   #Program counter
"TSC",  #Timestamp counter
"EAX",  #general purpose
]

class Registers():
    def __init__(self):
        for name in registers_names:
            setattr(self, name, 0)  #all registers at 0 on beggining
        self.PC= ram.OS_MEMORY_START   #except for PC

    def __repr__(self):
        content="   ".join([k+":"+str(v) for k,v in vars(self).items()])
        return "<Registers: "+content+">"
