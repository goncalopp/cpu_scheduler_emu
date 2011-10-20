import random
from timer import InternalTimer
import logging

class SimultaneousIO( Exception ):
    pass

class IO( InternalTimer ):
    def __init__(self, cpu, interrupt_number, io_operation_time):
        InternalTimer.__init__(self, cpu, interrupt_number)
        self.io_operation_time= io_operation_time

    def io_request(self):
        try:
            self.internalSetTimer( self.io_operation_time )
            logging.debug("IO request made")
        except AlreadyConfiguredException:
            raise SimultaneousIO()
    
    def step(self):
        try:
            self.internalStep()
        except InternalTimerEvent:
            logging.debug("IO interrupt triggered")
