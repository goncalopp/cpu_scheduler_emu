import machine

SCHEDULER_INTERRUPT=            machine.TIMER_INTERRUPT
DRIVER_IO_INTERUPT=             machine.IO_INTERRUPT
DRIVER_SYSCALL_INTERRUPT=       machine.SYSCALL_INTERRUPT_1
PROCESS_END_SYSCALL_INTERRUPT=  machine.SYSCALL_INTERRUPT_2

SCHEDULER_INTERRUPT_DURATION=           0
DRIVER_IO_INTERRUPT_DURATION=           0
DRIVER_SYSCALL_INTERRUPT_DURATION=      0
PROCESS_END_SYSCALL_INTERRUPT_DURATION= 0

class OS:
    def __init__(self, machine):
        self.machine= machine

    def setup_interrupt_vector(self):
        self.machine.set_interrupt_handler(  SCHEDULER_INTERRUPT, SCHEDULER_INTERRUPT_DURATION, self.scheduler_interrupt_handler)
        self.machine.set_interrupt_handler(  DRIVER_IO_INTERUPT, DRIVER_IO_INTERRUPT_DURATION, self.driver_io_interrupt_handler)
        self.machine.set_interrupt_handler(  DRIVER_SYSCALL_INTERRUPT, DRIVER_SYSCALL_INTERRUPT_DURATION, self.driver_syscall_interrupt_handler)
        self.machine.set_interrupt_handler(  PROCESS_END_SYSCALL_INTERRUPT, PROCESS_END_SYSCALL_INTERRUPT_DURATION, self.process_end_syscall_interrupt_handler)


    def scheduler_interrupt_handler(self):
        pass

    def process_end_syscall_interrupt_handler(self):
        pass

    def driver_syscall_interrupt_handler(self):
        pass

    def driver_io_interrupt_handler(self):
        pass
