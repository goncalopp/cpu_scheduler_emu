import logging
log= logging.getLogger('os')
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t%(module)s\t%(funcName)s\t%(message)s')
hdlr = logging.FileHandler('os.log.tsv', mode="w")
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)
from hardware import machine
from io_driver import IODriver
from timer_driver import TimerDriver
from scheduler import Scheduler
import interrupts 

class Kernel:
    def __init__(self, machine):
        self.machine= machine
        self.pid_counter=10
        self._initialize_subsystems()
        self._initialize_interrupt_handlers()
        log.debug("OS initialized")

    def _initialize_subsystems(self):
        self.io_driver=     IODriver( self )
        self.timer_driver=  TimerDriver( self )
        self.scheduler=     Scheduler( self )
        self.timer_driver.set_callback( self.scheduler.schedule )   #execute scheduler on timer interrupt

    def _initialize_interrupt_handlers(self):
        my_interrupt_handlers= [
                            self.timer_driver.timer_interrupt_handler,
                            self.io_driver.io_interrupt_handler,
                            self.io_driver.request_io,
                            self.scheduler.end_process_interrupt_handler,
                            self.scheduler.schedule,
                            ]
        mih, il= my_interrupt_handlers, interrupts.interrupt_list
        interrupts.InterruptHandlerGroup( self, self.machine, dict(zip(il, mih)))

    def generate_pid(self):
        n= self.pid_counter
        self.pidcounter+=1
        return n

    def get_system_ticks(self):
        return self.machine.get_clock_ticks()
