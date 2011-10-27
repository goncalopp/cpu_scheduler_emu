import logging
log= logging.getLogger('hardware')

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
    
    def internalSet( self, time ):
        '''interrupts cpu after TIME cpu steps'''
        assert type(time)==int
        assert time >= 1    #cannot interrupt cpu before concluding currently executing instruction
        if self.configured:
            raise AlreadyConfiguredException()
        self.time= time
        self.configured= True

    def internalUnset( self ):
        self.configured= False


class Timer( InternalTimer ):
    def set(self, time):
        self.internalSet( time )
        log.debug("timer set")
        
    def unset(self):
        self.internalUnset()
        
    def step(self):
        try:
            self.internalStep()
        except InternalTimerEvent:
            log.debug("timer interrupt was triggered ("+str(self.interrupt_number)+")")


