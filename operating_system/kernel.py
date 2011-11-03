import logging
log= logging.getLogger('os')
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t%(module)s\t%(funcName)s\t%(message)s')
hdlr = logging.FileHandler('os.log.tsv', mode="w")
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)
from hardware           import machine
from io_driver          import IODriver
from timer_driver       import TimerDriver
from dispatcher         import Dispatcher
from scheduler          import *
from loader             import Loader
from process_manager    import ProcessManager
from memory_allocator   import MemoryAllocator
import interrupts 

class Kernel:
    def __init__(self, machine):
        self.machine= machine
        self._initialize_subsystems()
        self._initialize_interrupt_handlers()
        log.debug("OS initialized")

    def _initialize_subsystems(self):
        self.memory_allocator=  MemoryAllocator         (self)
        self.loader=            Loader                  (self)
        self.io_driver=         IODriver                (self)
        self.timer_driver=      TimerDriver             (self)
        self.process_manager=   ProcessManager          (self)
        self.scheduler=         OOneScheduler           (self)
        self.dispatcher=        Dispatcher              (self)
        self.timer_driver.set_callback( self.dispatcher.timer_end )   #execute on timer interrupt

    def _initialize_interrupt_handlers(self):
        my_interrupt_handlers= [
                            self.timer_driver.timer_interrupt_handler,
                            self.io_driver.io_interrupt_handler,
                            self.io_driver.request_io,
                            self.dispatcher.remove_current_process,
                            ]
        mih, il= my_interrupt_handlers, interrupts.interrupt_list
        interrupts.InterruptHandlerGroup( self, self.machine, dict(zip(il, mih)))

    def get_system_ticks(self):
        return self.machine.get_clock_ticks()

    def kickstart(self):
        '''starts running the first process'''
        log.debug("kickstarting system")
        self.dispatcher.start_next_process()
