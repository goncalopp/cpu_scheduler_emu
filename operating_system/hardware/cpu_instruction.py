from cpu_interrupt import Interrupt

class InvalidInstruction( Exception ):
    pass

# [  X]  shall mean the value of register or instruction argument "X"
# [ *X]  shall mean the content of the memory address (PC)+(X), i.e:relative addressing

opcodes= \
    {
    "NOOP":     0,  #no operation
    "INT":      1,  #generate software interrupt [ARG1]
    "OFF":      2,  #"turn system off" (python exception) 
    "JNZ":      3,  #jump to [*ARG1] if [EAX] is not zero
    "LOAD":     4,  #load [ARG1]  (into EAX)
    "LOAD_REL": 5,  #load [*ARG1] (into EAX)
    "STOR":     6,  #write [EAX]  to [*ARG]
    "ADD":      7,  #add [ARG1]  to [EAX]
    "ADD_REL":  8,  #add [*ARG1] to [EAX]
    "JMP":      9,  #jump to [*ARG1]
    "JZ":      10,  #jump to [*ARG1] if [EAX] is zero
    }

optional_relative_addressing_opcodes=[4,7]
forced_relative_addressing_opcodes=[3,5,8,9,10]


#number of arguments of each instruction
number_of_arguments= \
    {
    0:0,
    1:1,
    2:0,
    3:1,
    4:1,
    5:1,
    6:1,
    7:1,
    8:1,
    9:1,
    }

class Program:
    def __init__(self, instructions, start_offset=0):
        assert all(map(lambda x:isinstance(x, Instruction), instructions))
        self.instructions= instructions
        self.start_offset= start_offset #start_offset marks the start of the "code segment" (and end of "data segment") 
    def __len__(self):
        return len(self.instructions)
    def __repr__(self):
        return "\n".join(map(str, self.instructions))

class Instruction:
    def __init__(self, op, *arguments):
        assert isinstance(op, int) or isinstance(op, Interrupt)
        assert all(map(lambda x:isinstance(x,int), arguments))
        self.op, self.args= op, arguments    #store arguments in list
    def __repr__(self):
        try:
            op= opcodes_reverse[self.op]
        except KeyError:
            try:
                op= str(int(self.op))
            except ValueError:
                raise InvalidInstruction(self.op)
        return "\t".join( [op]+map(str,self.args))

def instructionFromString(s):
    try:
        l= s.split()
        op, args= l[0], l[1:]
        try:
            op= opcodes[op] #was operation given as "assembly"?
        except KeyError:
            op= int(op)     #was operation given as numbers?
        args= map(int, args)
        #assert len(l)-1 == number_of_arguments[op]
        return Instruction( op, *args )
    except:
        raise InvalidInstruction(s)

def programFromString(s, start_offset=0):
    instructions=[]
    for line_number,line in enumerate(s.split("\n")):
        line_tokens= line.split()
        for token_number, token in enumerate(line_tokens):
            #translate absolute addressing to relative addressing
            if token.startswith("$"):
                abs_address= int(token[1:])
                rel_address=  abs_address - line_number +1
                line_tokens[ token_number ]= str( rel_address)
        line=" ".join(line_tokens)
        if len(line)>0: #ignore blank lines
            if "//" in line:
                line=line[:line.index("//")]    #remove comments
            instructions.append( instructionFromString(line) )
    return Program( instructions, start_offset )

opcodes_reverse= dict((v,k) for k, v in opcodes.items())    #construction dictionary from opcode to opname
for k,v in opcodes.items():                   #add opcodes as local variables
    locals()[k]=v
