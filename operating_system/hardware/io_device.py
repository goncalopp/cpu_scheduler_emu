import random
from timer import InternalTimer, InternalTimerEvent, AlreadyConfiguredException
import logging
log= logging.getLogger('hardware')

DEFAULT_IO_OPERATION_TIME= 100

class SimultaneousIO( Exception ):
    pass

class IO( InternalTimer ):
    def __init__(self, cpu, interrupt_number):
        InternalTimer.__init__(self, cpu, interrupt_number)
        self.io_operation_time= DEFAULT_IO_OPERATION_TIME
        self.used_clocks=0
        self.in_use=False

    def set_io_operation_time( self, n ):
        self.io_operation_time= n

    def io_request(self):
        try:
            self.internalSet( self.io_operation_time )
            self.in_use= True
            log.debug("request made")
        except AlreadyConfiguredException:
            raise SimultaneousIO()
    
    def step(self):
        if self.in_use:
            self.used_clocks+=1
        try:
            self.internalStep()
        except InternalTimerEvent:
            log.debug("IO interrupt triggered ("+str(self.interrupt_number)+")")
            self.in_use=False
