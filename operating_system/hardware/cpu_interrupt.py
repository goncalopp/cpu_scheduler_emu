class TaskConclusion( Exception ):
    pass
class TaskZeroDuration( Exception ):
    pass
class NoSuchInterrupt( Exception ):
    pass

class TaskClass:
    def __init__(self, task_name, task_duration, on_conclusion= lambda:None, on_step= lambda:None):
        self.task_name, self.task_duration, self.on_step, self.on_conclusion= task_name, task_duration, on_step, on_conclusion

class TaskInstance:
    def __init__( self, task_class):
        assert isinstance( task_class, TaskClass )
        self.task_class= task_class
        self.done=0
        self.concluded= False

    def step(self):
        if self.concluded:
            raise Exception("Stepping concluded task. If this ever occurs, cpu code is wrong")
        if self.task_class.task_duration==0:
            self.task_class.on_conclusion()
            raise TaskZeroDuration()
        self.done+= 1
        self.task_class.on_step()
        if self.done == self.task_class.task_duration:
            self.task_class.on_conclusion()
            self.concluded= True
            raise TaskConclusion();

class InterruptHandler( TaskClass ):
    def __init__(self, interrupt_number, interrupt_duration, on_conclusion):
        TaskClass.__init__(self, "[INTERRUPT "+str(interrupt_number)+"]", interrupt_duration, on_conclusion)
        assert type(interrupt_number)==int
        self.number= interrupt_number

class Interrupt( TaskInstance ):
    def __init__(self, handler):
        assert isinstance(handler, InterruptHandler)
        TaskInstance.__init__( self, handler )
