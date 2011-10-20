import logging

class TaskConclusionException( Exception ):
    pass
class TaskZeroDuration( Exception ):
    pass
class Multitask( Exception ):
    pass
class InterruptedInterruption( Exception ):
    pass


class TaskClass:
    def __init__(self, task_name, task_duration, on_conclusion= lambda:None, on_step= lambda:None):
        self.task_name, self.task_duration, self.on_step, self.on_conclusion= task_name, task_duration, on_step, on_conclusion

class Interrupt( TaskClass ):
    def __init__(self, interrupt_number, interrupt_duration, on_conclusion):
        TaskClass.__init__(self, "[INTERRUPT "+str(interrupt_number)+"]", interrupt_duration, on_conclusion)

class TaskInstance:
    def __init__( self, task_class):
        assert isinstance( task_class, TaskClass )
        self.task_class= task_class
        self.done=0
        self.concluded= False

    def step(self):
        if self.concluded:
            raise Exception("Stepping concluded task")
        if self.task_class.task_duration==0:
            self.task_class.on_conclusion()
            raise TaskZeroDuration()
        self.done+= 1
        self.task_class.on_step()
        if self.done == self.task_class.task_duration:
            self.task_class.on_conclusion()
            self.concluded= True
            raise TaskConclusionException();

class Cpu:
    def __init__(self, interrupt_vector=[]):
        assert all( map(lambda x:isinstance(x, Interrupt), interrupt_vector))
        self.interrupt_vector= interrupt_vector
        self.tsc=0
        self.tasks= []

    def _debug(self):
        return "CPU (tick "+str(self.tsc)+") "

    def step( self ):
        stepped= False
        while not stepped:
                try:
                    self.tasks[0].step()
                    logging.info(self._debug()+self.tasks[0].task_class.task_name+" (step)")
                    stepped= True
                except IndexError:
                    #no tasks
                    logging.warning(self._debug()+"NO TASK")
                    stepped=True
                except TaskConclusionException:
                    logging.info(self._debug()+self.tasks[0].task_class.task_name+" (step and conclude)")
                    self.tasks.pop(0)
                    stepped= True
                except TaskZeroDuration:
                    logging.info(self._debug()+self.tasks[0].task_class.task_name+" (completed in 0 ticks)")
                    self.tasks.pop(0)
        self.tsc+=1

    def add_task( self, taskclass ):
        if sum(map( lambda t:not isinstance(t.task_class, Interrupt), self.tasks)) > 0:
            raise Multitask("Cannot have more than one task on cpu")
        logging.debug("CPU added task of TaskClass "+taskclass.task_name)
        assert isinstance(taskclass, TaskClass)
        task= TaskInstance( taskclass )
        self.tasks.append(task)

    def interrupt( self, interrupt_number ):
        if sum(map( lambda t:isinstance(t.task_class, Interrupt), self.tasks)) > 0:
            raise InterruptedInterruption("Cannot have multiple interrupts running")
        try:
            task= TaskInstance( self.interrupt_vector[ interrupt_number ] )
            self.tasks.insert(0, task)          # a interrupt is immediatly executed
            logging.debug("CPU interrupt "+str(interrupt_number))
        except IndexError:
            raise Exception("No such interrupt: "+str(interrupt_number))

    def set_interrupt_handler(self, interrupt_number, cpu_clock_duration, function):
        self.interrupt_vector[ interrupt_number ]= Interrupt( interrupt_number, cpu_clock_duration, function )
    
