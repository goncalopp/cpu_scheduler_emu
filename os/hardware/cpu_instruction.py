class UnknownOpcode( Exception ):
    pass

opcodes= \
    {
    "NOOP": 0,  #no operation
    "INT": 1,   #generate software interrupt [a1]
    "OFF": 2,   #"turn system off" (python exception) 
    }
    
for k,v in opcodes.items():
    locals()[k]=v

class Instruction:
    def __init__(self, op, a1):
        self.op, self.a1= op, a1
