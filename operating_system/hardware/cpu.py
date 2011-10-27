from cpu_interrupt import *
from cpu_instruction import *
from cpu_registers import *
import logging
log= logging.getLogger('hardware')

class Poweroff( Exception ):
    pass

class TaskStateSegment:
    SAVED_REGISTERS=["PC","EAX"]
    def __init__(self, cpu=None):
        if cpu!=None:
            self.save_state( cpu )
        else:
            self.create_state()

    def save_state( self, cpu ):
        assert isinstance(cpu, Cpu)
        for name in self.SAVED_REGISTERS:
            setattr(self, name, getattr(cpu.registers, name))

    def load_state( self, cpu ):
        assert isinstance(cpu, Cpu)
        for name in self.SAVED_REGISTERS:
            setattr(cpu.registers, name, getattr(self, name))

    def create_state(self):
        for name in self.SAVED_REGISTERS:
            setattr(self, name, 0)

class Cpu:
    def __init__(self, memory):
        self.registers= Registers()
        self.memory= memory
        self.tss= None          #task state segment, keeps old cpu state when context switching

    def _save_tss(self):
        self.tss= TaskStateSegment( self )

    def clear_tss(self):
        self.tss=None

    def context_switch(self, old_tss):
        '''loads information of an TSS into current cpu state'''
        assert isinstance(old_tss, TaskStateSegment)
        old_tss.load_state( self )

    def _debug(self):
        return str(self.registers)
        
    def _rel(self, n):
        return self.registers.PC + n

    def step( self ):
        log.info("-----------------CPU STEP START-----------------")
        stepped= False
        while not stepped:
            if self.registers.INT:
                #executing interruption
                try:
                    self.registers.INT.step()
                    log.info(self._debug()+self.registers.INT.task_class.task_name+" interrupt (step)")
                    stepped= True
                except TaskConclusion:
                    log.info(self._debug()+self.registers.INT.task_class.task_name+" (interrupt step and conclude)")
                    self.tasks.pop(0)
                    stepped= True
                except TaskZeroDuration:
                    log.info(self._debug()+self.registers.INT.task_class.task_name+" (interrupt completed in 0 ticks)")
                    self.registers.INT= None
            else:
                #not executing interruption
                log.info(self._debug())
                self.execute_instruction( self.memory[self.registers.PC] )
                stepped=True
        self.registers.TSC+=1

    def execute_instruction(self, i):
        assert isinstance(i, Instruction)
        log.debug("executing instruction: "+str(i))
        op, args= i.op, i.args
        if op==NOOP:
            pass
        elif op==INT:
            self.interrupt(args[0])
        elif op==OFF:
            raise Poweroff()
        elif op==JMP:
                self.registers.PC+= args[0] - 1 # -1 since we will increment PC after the JMP
        elif op==JNZ:
            if self.registers.EAX!=0:
                self.registers.PC+= args[0] - 1 # -1 since we will increment PC after the JMP
        elif op==JZ:
            if self.registers.EAX==0:
                self.registers.PC+= args[0] - 1 # -1 since we will increment PC after the JMP
        elif op==LOAD:
            self.registers.EAX= args[0]
        elif op==LOAD_REL:
            self.registers.EAX= self.memory[self._rel(args[0])].op
        elif op==STOR:
            self.memory[ self._rel(args[0]) ]=  Instruction(self.registers.EAX)
        elif op==ADD:
            self.registers.EAX+= args[0]
        elif op==ADD_REL:
            self.registers.EAX+= self.memory.read( self._rel(args[0]) ).op
        else:
            raise InvalidInstruction()
        self.registers.PC+=1
        
    def interrupt( self, interrupt_number ):
        if self.registers.INT:
            raise InterruptedInterruption("Cannot have multiple interrupts running")
        try:
            self.registers.INT= TaskInstance( self.memory._read_interrupt_handler(interrupt_number) )
            self._save_tss()    #each time an interruption is executed, the TSS is saved
            log.debug("generated interrupt "+str(interrupt_number))
        except:
            raise NoSuchInterrupt("Error running interrupt: "+str(interrupt_number))

    def set_interrupt_handler(self, interrupt_number, cpu_clock_duration, function):
        self.memory._write_interrupt_handler( interrupt_number, Interrupt(str(interrupt_number), cpu_clock_duration, function))
    
