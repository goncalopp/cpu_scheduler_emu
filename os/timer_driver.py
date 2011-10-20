class TimerDriver:
    def __init__(self, os):
        self.os= os
        self.callback= lambda : None

    def set_timer( self, n ):
        os.machine.timer.setTimer( n )
        
    def set_callback( self, f ):
        assert callable(f)
        self.callback= f

    def timer_interrupt_handler(self):
        self.callback()
