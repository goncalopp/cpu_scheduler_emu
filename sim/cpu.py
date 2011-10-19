import logging

class TaskConclusionException( Exception ):
    pass
class TaskZeroDuration( Exception ):
    pass

class CpuTask:
    def __init__(self, task_name, task_duration, on_conclusion= lambda:None, on_step= lambda:None):
        self.task_name, self.task_duration, self.on_step, self.on_conclusion= task_name, task_duration, on_step, on_conclusion
        self.done=0
        self.concluded= False

    def step(self):
        if self.concluded:
            raise Exception("Stepping concluded task")
        if self.task_duration==0:
            self.on_conclusion()
            raise TaskZeroDuration()
        self.done+= 1
        self.on_step()
        if self.done == self.task_duration:
            self.on_conclusion()
            self.concluded= True
            raise TaskConclusionException();

class Cpu:
    def __init__(self):
        self.rtc=0
        self.tasks= []
        self.step_functions= []

    def step( self ):
        stepped= False
        while not stepped:
                try:
                    self.tasks[0].step()
                    logging.info("CPU stepped: "+self.tasks[0].task_name)
                    stepped= True
                except IndexError:
                    #no tasks
                    logging.warning("CPU stepped while executing no task")
                    stepped=True
                except TaskConclusionException:
                    logging.info("CPU stepped and concluded: "+self.tasks[0].task_name)
                    self.tasks.pop(0)
                    stepped= True
                except TaskZeroDuration:
                    logging.info("CPU completed task in 0 clocks: "+self.tasks[0].task_name)
                    self.tasks.pop(0)
        self.rtc+=1
        for f in self.step_functions: #step all functions we were required to, on instantiation
            f()
            
    def add_task( self, task ):
        assert isinstance(task, CpuTask)
        self.tasks.append(task)
        
    def interrupt( self, task ):
        assert isinstance(task, CpuTask)
        task.task_name+=" [INTERRUPT]"
        self.tasks.insert(0, task)          # a interrupt is immediatly executed
        
    def add_step_callback(self, f):
        self.step_functions.append( f )
    
    def remove_step_callback(self, f):
        self.step_functions.remove( f )
    
