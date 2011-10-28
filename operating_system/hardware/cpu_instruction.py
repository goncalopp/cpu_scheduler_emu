from cpu_interrupt import Interrupt
from ram import RAM
from ram_cell import RamCell, Instruction

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

opcodes_reverse= dict((v,k) for k, v in opcodes.items())    #construction dictionary from opcode to opname
for k,v in opcodes.items():                   #add opcodes as local variables
    locals()[k]=v

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
        data_segment, code_segment= instructions[:start_offset], instructions[start_offset:]
        assert all(map(lambda x:isinstance(x, RamCell), code_segment))
        assert all(map(lambda x:isinstance(x, Instruction), code_segment))
        self.instructions= instructions
        self.start_offset= start_offset #start_offset marks the start of the "code segment" (and end of "data segment") 

    def writeToRam(self, ram, offset):
        assert isinstance(ram, RAM)
        for i,instruction in enumerate(self.instructions):
            ram.raw_write(offset+i, instruction)

    def __len__(self):
        return len(self.instructions)

    def __repr__(self):
        return "\n".join(map(str, self.instructions))

    def __getitem__(self, k):
        return self.instructions[k]

def instructionFromString(s):
    l= s.split()
    op, args= l[0], map(int,l[1:])
    try:
        op= opcodes[op] #was op "assembly"?
        return Instruction(op, *args)
    except KeyError:
        try:
            assert len(args)==0
            op= int(op)
            return RamCell(op)
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

