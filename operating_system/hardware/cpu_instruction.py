class InvalidInstruction( Exception ):
    pass

opcodes= \
    {
    "NOOP": 0,  #no operation
    "INT": 1,   #generate software interrupt [a1]
    "OFF": 2,   #"turn system off" (python exception) 
    }

#number of arguments of each instruction
number_of_arguments= \
    {
    0:0,
    1:1,
    2:0,
    }

class Program:
    def __init__(self, instructions, start_offset=0):
        assert all(map(lambda x:isinstance(x, Instruction), instructions))
        self.instructions= instructions
        self.start_offset= start_offset #start_offset marks the start of the "code segment" (and end of "data segment") 
    def __len__(self):
        return len(self.instructions)

class Instruction:
    def __init__(self, op, *arguments):
        self.op, self.args= op, arguments    #store arguments in list
    def __repr__(self):
        try:
            op= opcodes_reverse[self.op]
        except KeyError:
            try:
                op= str(int(self.op))
            except:
                raise InvalidInstruction(self.op)
        return "\t".join( [op]+map(str,self.args))

def instructionFromString(s):
    try:
        l= s.split("\t")
        op, args= l[0], l[1:]
        args= map(int, args)
        try:
            op= opcodes[op] #was operation given as "assembly"?
        except KeyError:
            op= int(op)     #was operation given as numbers?
        assert len(l)-1 == number_of_arguments[op]
        return Instruction( op, *args )
    except:
        raise InvalidInstruction(s)

def programFromString(s):
    instructions=[]
    for line in s.split("\n"):
        instructions.append( instructionFromString(line) )
    return Program( instructions)

opcodes_reverse= dict((v,k) for k, v in opcodes.items())    #construction dictionary from opcode to opname
for k,v in opcodes.items():                   #add opcodes as local variables
    locals()[k]=v
