class UnknownOpcode( Exception ):
    pass

opcodes= \
    {
    "NOOP": 0,  #no operation
    "INT": 1,   #generate software interrupt [a1]
    "OFF": 2,   #"turn system off" (python exception) 
    }

class Program:
    def __init__(self, instructions):
        assert all(map(lambda x:isinstance(x, Instruction), instructions))
        self.instructions= instructions
    def __len__(self):
        return len(self.instructions)

class Instruction:
    def __init__(self, op, a1=0):
        self.op, self.a1= op, a1
    def __repr__(self):
        try:
            return "\t".join( (opcodes_reverse[self.op], str(self.a1)) )
        except KeyError:
            raise UnknownOpcode()

def instructionFromString(s):
    try:
        l= s.split("\t")
        op= l[0]
        if len(l)==1:
            a1= 0
        else:
            a1= l[1]
        a1= int(a1)
        try:
            op= opcodes[op] #was operation given as "assembly"?
        except KeyError:
            op= int(op)     #was operation given as numbers?
        return Instruction( op, a1 )
    except:
        raise UnknownOpcode(s)

def programFromString(s):
    instructions=[]
    for line in s.split("\n"):
        instructions.append( instructionFromString(line) )
    return Program( instructions)

opcodes_reverse= dict((v,k) for k, v in opcodes.items())    #construction dictionary from opcode to opname
for k,v in opcodes.items():                   #add opcodes as local variables
    locals()[k]=v
