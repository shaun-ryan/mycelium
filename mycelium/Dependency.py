from .Task import Task, TaskStatus
from .DependencyStatus import *


class Dependency:

    def __init__(self, task:Task, 
        condition:str=DependencyCondition.COMPLETION.name, 
        operator:str=DependencyOperator.OR.name):

        self.operator = DependencyOperator[operator.upper()]
        self.condition = DependencyCondition[condition.upper()]
        self.task = task

    def toDict(self):
        return {
            "task": self.task.name,
            "condition": self.condition.name,
            "operator": self.operator.name
        }


    def isReady(self)->bool:

        if self.task.status.value < TaskStatus.SUCEEDED.value:
            return False

        elif self.task.status.value >= TaskStatus.SUCEEDED.value and \
        self.condition == DependencyCondition.COMPLETION:
            
            return True

        elif self.task.status == TaskStatus.SUCEEDED and \
        self.condition == DependencyCondition.SUCCESS:

           return True

        elif self.task.status == TaskStatus.FAILED and \
        self.condition == DependencyCondition.FAILURE:

           return True
           
        else:
            return False
        

