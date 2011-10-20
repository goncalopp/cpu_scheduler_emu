import machine

SCHEDULER_INTERRUPT=            machine.TIMER_INTERRUPT
DRIVER_IO_INTERUPT=             machine.IO_INTERRUPT
DRIVER_SYSCALL_INTERRUPT=       machine.SYSCALL_INTERRUPT_1
PROCESS_END_SYSCALL_INTERRUPT=  machine.SYSCALL_INTERRUPT_2

SCHEDULER_INTERRUPT_DURATION=           0
DRIVER_IO_INTERRUPT_DURATION=           0
DRIVER_SYSCALL_INTERRUPT_DURATION=      0
PROCESS_END_SYSCALL_INTERRUPT_DURATION= 0

def setup_interrupt_vector(machine):
    machine.set_interrupt_handler(  SCHEDULER_INTERRUPT,
                                    SCHEDULER_INTERRUPT_DURATION,
                                    scheduler_interrupt_handler)
    machine.set_interrupt_handler(  DRIVER_IO_INTERUPT,
                                    DRIVER_IO_INTERRUPT_DURATION,
                                    driver_io_interrupt_handler)
    machine.set_interrupt_handler(  DRIVER_SYSCALL_INTERRUPT,
                                    DRIVER_SYSCALL_INTERRUPT_DURATION,
                                    driver_syscall_interrupt_handler)
    machine.set_interrupt_handler(  PROCESS_END_SYSCALL_INTERRUPT,
                                    PROCESS_END_SYSCALL_INTERRUPT_DURATION,
                                    process_end_syscall_interrupt_handler)


def scheduler_interrupt_handler():
    pass

def process_end_syscall_interrupt_handler():
    pass

def driver_syscall_interrupt_handler():
    pass

def driver_io_interrupt_handler():
    pass
