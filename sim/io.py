import random
from timer import InternalTimer

class SimultaneousIO( Exception ):
    pass

class IO( InternalTimer ):
    def __init__(cpu, interrupt_number, read_time, write_time):
        InternalTimer.__init__(self, cpu, interrupt_number)
        self.read_time, self.write_time= read_time, write_time

    def read(self):
        try:
            self.internalSetTimer( self.read_time )
        except AlreadyConfiguredException:
            raise SimultaneousIO()

    def write(self):
        try:
            self.internalSetTimer( self.write_time )
        except AlreadyConfiguredException:
            raise SimultaneousIO()
