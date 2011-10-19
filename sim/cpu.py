import logging

class ConclusionException( Exception ):
    pass

class CpuTask:
    def __init__(self, task_name, task_duration, on_step= lambda:None, on_conclusion= lambda:None):
        self.task_name, self.task_duration, self.on_step, self.on_conclusion= task_name, task_duration, on_step, on_conclusion
        self.done=0
        self.concluded= False

    def step(self):
        if self.concluded:
            raise Exception("Stepping concluded task")
        self.done+= 1
        self.on_step()
        if self.done == self.task_duration:
            self.on_conclusion()
            self.concluded= True
            raise ConclusionException();

class Cpu:
    def __init__(self, step_functions=[]):
        self.rtc=0
        self.tasks= []
        self.step_functions= step_functions

    def step( self ):
        self.rtc+=1
        if len(tasks)==0:
            logging.warning("CPU stepped while executing no task")
        else:
            try:
                self.tasks[0].step()
                logging.info("CPU stepped executing "+self.tasks[0].task_name)
            except ConclusionException:
                logging.info("CPU task concluded: "+self.tasks[0].task_name)
                self.tasks.pop(0)
                
        for f in self.step_functions(): #step all functions we were required to, on instantiation
            f()
            
    def add_task( self, task ):
        assert isinstance(task, CpuTask)
        self.tasks.append(task)
        
    def interrupt( self, task ):
        assert isinstance(task, CpuTask)
        task.task_name+=" [INTERRUPT]"
        self.tasks.insert(0, task)          # a interrupt is immediatly executed
        
    
    
