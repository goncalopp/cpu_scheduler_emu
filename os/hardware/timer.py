import logging

class AlreadyConfiguredException( Exception ):
    pass
class InternalTimerEvent( Exception ):
    pass
    
class InternalTimer:
    '''raises a interrupts after a given time has passed'''
    def __init__(self, cpu, interrupt_number):
        self.cpu, self.interrupt_number= cpu, interrupt_number
        self.configured= False
    
    def internalStep(self):
        if self.configured:
            self.time-=1
            if self.time==0:
                self.cpu.interrupt( self.interrupt_number )
                self.configured= False
                raise InternalTimerEvent()
    
    def internalSetTimer( self, time ):
        '''interrupts cpu after TIME cpu steps'''
        assert time >= 1    #cannot interrupt cpu before concluding currently executing instruction
        if self.configured:
            raise AlreadyConfiguredException()
        self.time= time
        self.configured= True


class Timer( InternalTimer ):
    def setTimer(self, time):
        self.internalSetTimer( time)
        
    def step(self):
        try:
            self.internalStep()
        except InternalTimerEvent:
            logging.debug("TIMER  interrupt triggered")


