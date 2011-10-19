import logging

class AlreadyConfiguredException( Exception ):
    pass

class Timer:
    def __init__(self, cpu, interrupt_number):
        self.cpu, self.interrupt_number= cpu, interrupt_number
        self.configured= False

    def step(self):
        if self.configured:
            self.time-=1
            if self.time==0:
                logging.debug("TIMER triggered")
                self.cpu.interrupt( self.interrupt_number )
                self.configured= False

    def configure( self, time ):
        '''interrupts cpu after TIME cpu steps'''
        assert time >= 1    #cannot interrupt cpu before concluding currently executing instruction
        if self.configured:
            raise AlreadyConfiguredException()
        else:
            logging.debug("TIMER configured to generate interrupt in "+str(time)+" clocks")
            self.time= time
            self.configured= True
