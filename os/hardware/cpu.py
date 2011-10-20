import logging

class TaskConclusionException( Exception ):
    pass
class TaskZeroDuration( Exception ):
    pass


class TaskClass:
    def __init__(self, task_name, task_duration, on_conclusion= lambda:None, on_step= lambda:None):
        self.task_name, self.task_duration, self.on_step, self.on_conclusion= task_name, task_duration, on_step, on_conclusion

class Interrupt( TaskClass ):
    def __init__(self, interrupt_number, interrupt_duration, on_conclusion):
        TaskClass.__init__(self, str(interrupt_number)+" [INTERRUPT]", interrupt_duration, on_conclusion)

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

    def step( self ):
        stepped= False
        while not stepped:
                try:
                    self.tasks[0].step()
                    logging.info("CPU stepped: "+self.tasks[0].task_class.task_name)
                    stepped= True
                except IndexError:
                    #no tasks
                    logging.warning("CPU stepped while executing no task")
                    stepped=True
                except TaskConclusionException:
                    logging.info("CPU stepped and concluded: "+self.tasks[0].task_class.task_name)
                    self.tasks.pop(0)
                    stepped= True
                except TaskZeroDuration:
                    logging.info("CPU completed task in 0 clocks: "+self.tasks[0].task_class.task_name)
                    self.tasks.pop(0)
        self.tsc+=1
            
    def add_task( self, taskclass ):
        logging.debug("CPU added task of TaskClass "+taskclass.task_name)
        assert isinstance(taskclass, TaskClass)
        task= TaskInstance( taskclass )
        self.tasks.append(task)

    def interrupt( self, interrupt_number ):
        try:
            task= TaskInstance( self.interrupt_vector[ interrupt_number ] )
            self.tasks.insert(0, task)          # a interrupt is immediatly executed
            logging.debug("CPU interrupt "+str(interrupt_number))
        except IndexError:
            raise Exception("No such interrupt: "+str(interrupt_number))

    def set_interrupt_handler(self, interrupt_number, cpu_clock_duration, function):
        self.interrupt_vector[ interrupt_number ]= Interrupt( interrupt_number, cpu_clock_duration, function )
    
