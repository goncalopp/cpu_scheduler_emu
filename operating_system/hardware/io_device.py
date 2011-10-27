import random
from timer import InternalTimer, InternalTimerEvent
import logging
log= logging.getLogger('hardware')

DEFAULT_IO_OPERATION_TIME= 100

class SimultaneousIO( Exception ):
    pass

class IO( InternalTimer ):
    def __init__(self, cpu, interrupt_number):
        InternalTimer.__init__(self, cpu, interrupt_number)
        self.io_operation_time= DEFAULT_IO_OPERATION_TIME

    def set_io_operation_time( self, n ):
        self.io_operation_time= n

    def io_request(self):
        try:
            self.internalSetTimer( self.io_operation_time )
            log.debug("request made")
        except AlreadyConfiguredException:
            raise SimultaneousIO()
    
    def step(self):
        try:
            self.internalStep()
        except InternalTimerEvent:
            log.debug("IO interrupt triggered ("+str(self.interrupt_number)+")")
