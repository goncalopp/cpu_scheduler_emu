import logging
log= logging.getLogger('os')

class TimerDriver:
    def __init__(self, os):
        log.debug("initializing timer driver")
        self.os= os
        self.callback= lambda : None

    def set_timer( self, n ):
        self.os.machine.timer.set( n )
        log.debug("timer set to "+str(n))
        
    def unset_timer( self ):
        self.os.machine.timer.unset()

    def set_callback( self, f ):
        assert callable(f)
        self.callback= f

    def timer_interrupt_handler(self):
        log.debug("handling interrupt")
        self.callback()
