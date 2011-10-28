class RamCell:
    def __init__(self, value):
        from cpu_interrupt import InterruptHandler
        assert type(value)==int or isinstance(value, InterruptHandler)   #hack to save python in memory cells
        self.op= value
    def __repr__(self):
        return "MemoryCell: "+str( self.op )

class Instruction(RamCell):
    def __init__(self, op, *arguments):
        from cpu_instruction import opcodes
        assert all(map(lambda x:isinstance(x,int), arguments))  #all arguments are int
        assert op in opcodes.values()
        RamCell.__init__(self, op)
        self.args= arguments            #store arguments in list
    def __repr__(self):
            from cpu_instruction import opcodes_reverse
            try:
                op= str(opcodes_reverse[self.op])
                return "\t".join( [op]+map(str,self.args))
            except KeyError:
                raise InvalidInstruction(self.op)
