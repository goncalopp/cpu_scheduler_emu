class UnknownOpcode( Exception ):
    pass

opcodes= \
    {
    "NOOP": 0,
    "INT": 1,
    }
    
for k,v in opcodes.items():
    locals()[k]=v

class Instruction:
    def __init__(self, op, a1):
        self.op, self.a1= op, a1
