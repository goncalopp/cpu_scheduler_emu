class UnknownOpcode( Exception ):
    pass

opcodes= \
    {
    "NOOP": 0,  #no operation
    "INT": 1,   #generate software interrupt [a1]
    "OFF": 2,   #"turn system off" (python exception) 
    }

class Instruction:
    def __init__(self, op, a1):
        self.op, self.a1= op, a1
    def __repr__(self):
        try:
            return "\t".join( (opcodes_reverse[self.op], str(self.a1)) )
        except KeyError:
            raise UnknownOpcode()

def instructionFromString(s):
    try:
        op, a1= s.split("\t")
        a1= int(a1)
        op= opcodes[op]
        return Instruction(op, a1)
    except KeyError:
            raise UnknownOpcode()


opcodes_reverse= dict((v,k) for k, v in opcodes.items())    #construction dictionary from opcode to opname
for k,v in opcodes.items():                   #add opcodes as local variables
    locals()[k]=v
