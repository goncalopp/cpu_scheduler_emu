import logging
from cpu import Cpu, CpuTask

class AlreadyConfiguredException( Exception ):
    pass

class Timer:
    def __init__(self, cpu):
        assert isinstance(cpu, Cpu)
        self.cpu= cpu
        self.task= None
        cpu.add_step_callback( self.step )

    def step(self):
        if not self.task is None:
            self.time-=1
            if self.time==0:
                logging.debug("TIMER triggered, interrupting cpu with "+self.task.task_name)
                self.cpu.interrupt( self.task )
                self.task= None

    def configure( self, task, time ):
        '''executes a given task after TIME cpu steps'''
        assert time >= 1    #cannot interrupt cpu before concluding currently executing instruction
        if not self.task is None:
            raise AlreadyConfiguredException()
        else:
            logging.debug("TIMER configured to interrupt with "+task.task_name+" in "+str(time)+" clocks")
            self.task= task
            self.time= time
