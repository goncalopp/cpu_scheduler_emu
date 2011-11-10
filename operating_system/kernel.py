USE_IDLE_PROCESS= True

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
from dispatcher         import Dispatcher, NotExecutingAnything
from scheduler          import RoundRobinScheduler, OOneScheduler, StrideScheduler
from loader             import Loader
from process_manager    import ProcessManager
from memory_allocator   import MemoryAllocator
from idle_process       import IdleProcessScheduler
from pcb                import RUNNABLE
import interrupts 

SCHEDULER_CLASS= StrideScheduler

class Kernel:
    def __init__(self, machine):
        self.machine= machine
        self._initialize_subsystems()
        log.debug("OS initialized")

    def _initialize_subsystems(self):
        self.memory_allocator=  MemoryAllocator         (self)
        self.io_drivers= [IODriver(self, self.machine.ios[x]) for x in xrange(self.machine.NUMBER_OF_IO_DEVICES)]
        self.timer_driver=      TimerDriver             (self)
        self.process_manager=   ProcessManager          (self)
        self.scheduler=         SCHEDULER_CLASS         (self)
        self.dispatcher=        Dispatcher              (self)
        self._initialize_interrupt_handlers()
        self.loader=            Loader                  (self)
        self.timer_driver.set_callback( self.dispatcher.swap_processes )   #execute on timer interrupt
        if USE_IDLE_PROCESS:
            IdleProcessScheduler    (self)

    def _initialize_interrupt_handlers(self):
        self.interrupt_handlers= interrupts.InterruptHandlerGroup(self)
        my_interrupt_handlers= \
        [self.timer_driver.timer_interrupt_handler,  self.dispatcher.remove_current_process]+\
        [self.io_drivers[x].io_interrupt_handler for x in xrange(self.machine.NUMBER_OF_IO_DEVICES)]+\
        [self.io_drivers[x].request_io for x in xrange(self.machine.NUMBER_OF_IO_DEVICES)]
        mih, il= my_interrupt_handlers, self.interrupt_handlers.interrupt_list
        self.interrupt_handlers.set_handlers( dict(zip(il, mih)))

    def get_system_ticks(self):
        return self.machine.get_clock_ticks()

    def kickstart(self):
        '''starts running the first process'''
        log.debug("kickstarting system")
        self.dispatcher.start_next_process()

    def shutdown(self):
        '''shuts down system'''
        log.info("Shutting down")
        try:
            running= self.dispatcher.stop_running_process()
            running.changeState( RUNNABLE )
            self.scheduler.enqueue( running )   #must, to preserve consistency. We'll remove it on the next for cycle
        except NotExecutingAnything:
            pass
        for process in self.process_manager.get_all_processes():
                self.process_manager.remove_process( process.pid )
        for k in vars(self).keys(): #just to preserve an eventual
            delattr(self, k)        #debugger's sanity
