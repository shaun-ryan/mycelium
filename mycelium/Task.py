from abc import ABC, abstractmethod
from time import sleep
from enum import Enum
import json
from .DependencyStatus import DependencyCondition, DependencyOperator
from . import Logging


class TaskStatus(Enum):
    NONE = 1
    QUEUED = 2
    EXECUTING = 3
    SUCEEDED = 4
    FAILED = 5


class Task(ABC):


    @staticmethod
    def taskFactory(task:dict):
        if task["type"] == "databricksNotebook":
            return DatabricksNotebook(**task)
        elif task["type"] == "databricksLibrary":
            return DatabricksLibrary(**task)


    @property
    @abstractmethod
    def status(self)->TaskStatus:
        pass


    @property
    @abstractmethod
    def name(self)->str:
        pass


    @property
    @abstractmethod
    def enabled(self)->bool:
        pass


    @property
    @abstractmethod
    def type(self)->str:
        pass


    @property
    @abstractmethod
    def dependents(self)->list:
        pass


    @property
    @abstractmethod
    def dependencies(self)->list:
        pass


    @abstractmethod
    def execute(self)->dict:
        pass


    @abstractmethod
    def isReady(self)->bool:
        pass


class DatabricksNotebook(Task):


    def __init__(self,
                type:str,
                name:str,
                path:str = "./",
                timeout:int = 3600,
                transformation:str = "default",
                enabled:bool = True,
                retry:int = 0,
                parameters:dict = None):

        self.status = TaskStatus.NONE
        self.type = type
        self.name = name
        self.path = path
        self.timeout = timeout
        self.transformation = transformation
        self.enabled = enabled
        self.retry = retry
        self.parameters = parameters
        self.dependencies = list()
        self.dependents = list()
    

    @property
    def status(self)->TaskStatus:
        return self._status


    @status.setter
    def status(self, value:TaskStatus):
        self._status = value


    @property
    def name(self)->str:
        return self._name


    @name.setter
    def name(self, value:str):
        self._name = value


    @property
    def enabled(self)->bool:
        return self._enabled


    @enabled.setter
    def enabled(self, value:bool):
        self._enabled = value


    @property
    def type(self)->str:
        return self._type


    @type.setter
    def type(self, value:str):
        self._type = value


    @property
    def dependencies(self)->list:
        return self._dependencies


    @dependencies.setter
    def dependencies(self, value:list):
        self._dependencies = value


    @property
    def dependents(self)->list:
        return self._dependents


    @dependents.setter
    def dependents(self, value:list):
        self._dependents = value


    def execute(self):

        logger = Logging.getLogger(self.name)
        self.status = TaskStatus.EXECUTING

        try:
            logger.info(f"Started Executing {self.__class__.__name__}: {self.name}")
            sleep(2)
            logger.info(f"Succeeded Executing {self.__class__.__name__}: {self.name}")
            self.status = TaskStatus.SUCEEDED

        except:
            logger.warning(f"Failed Executing {self.__class__.__name__}: {self.name}")
            self.status = TaskStatus.FAILED

        return dict()


    def isReady(self)->bool:
        """work out if it's ok to process. 
        
        The task is ready when all of it's dependencies are full filled
        and that it's not already queued."""

        andDependencies = [d.isReady() for d in self.dependencies if d.operator == DependencyOperator.AND]
        orDependencies = [d.isReady() for d in self.dependencies if d.operator == DependencyOperator.OR]

        if not andDependencies:
            andDependencies = []

        if not orDependencies:
            orDependencies = []
        
        ready = (all(andDependencies) or any(orDependencies)) and self.status == TaskStatus.QUEUED
        # print(f"task:{self.name}, ready:{ready}, and:{all(andDependencies)}, or:{any(orDependencies)}, status:{self.status.name}")

        return ready


    def toDict(self):
        return {
            "name" : self.name ,
            "status" : self.status.name,
            "type" : self.type,
            "path" : self.path,
            "timeout" : self.timeout,
            "transformation" : self.transformation,
            "enabled" : self.enabled,
            "retry" : self.retry,
            "parameters" : self.parameters,
            "dependents": [d.name for d in self.dependents],
            "dependencies": [d.toDict() for d in self.dependencies]
        }


    def __str__(self):

        return json.dumps(self.toDict(), indent=4)
        

class DatabricksLibrary(Task):


    def __init__(self, type:str, name:str):

        self.status = TaskStatus.NONE
        self.type = type
        self.name = name
        self.enabled = True
        self.dependencies = []
        self.dependents = []


    @property
    def status(self)->TaskStatus:
        return self._status


    @status.setter
    def status(self, value:TaskStatus):
        self._status = value


    @property
    def name(self)->str:
        return self._name


    @name.setter
    def name(self, value:str):
        self._name = value


    @property
    def enabled(self)->bool:
        return self._enabled


    @enabled.setter
    def enabled(self, value:bool):
        self._enabled = value


    @property
    def type(self)->str:
        return self._type


    @type.setter
    def type(self, value:str):
        self._type = value


    @property
    def dependencies(self)->list:
        return self._dependencies


    @dependencies.setter
    def dependencies(self, value:list):
        self._dependencies = value


    @property
    def dependents(self)->list:
        return self._dependents


    @dependents.setter
    def dependents(self, value:list):
        self._dependents = value


    def execute(self):
        logger = Logging.getLogger(self.name)
        logger.info(f"Started Executing {self.__class__.__name__}: {self.name}")
        sleep(5)
        logger.info(f"Finished Executing {self.__class__.__name__}: {self.name}")
        return dict()


    def isReady(self)->bool:
        """work out if it's ok to process. 
        
        The task is ready when all of it's dependencies are full filled
        and that it's not already queued."""

        # get the and or dependencies separately so they can be tested separately
        andDependencies = [d.isReady() for d in self.dependencies if d.operator == DependencyOperator.AND]
        orDependencies = [d.isReady() for d in self.dependencies if d.operator.name == DependencyOperator.OR]

        # should always be assigned but for safety
        if not andDependencies:
            andDependencies = []

        if not orDependencies:
            orDependencies = []

        # logically evaluate and return
        return (all(andDependencies) or any(orDependencies)) and currentStatus == TaskStatus.NONE



class PipelineOrigin(Task):

    def __init__(self, type:str, name:str):

        self.status = TaskStatus.NONE
        self.type = type
        self.name = name
        self.enabled = True
        self.dependents = []


    @property
    def status(self)->TaskStatus:
        return self._status


    @status.setter
    def status(self, value:TaskStatus):
        self._status = value


    @property
    def name(self)->str:
        return self._name


    @name.setter
    def name(self, value:str):
        self._name = value


    @property
    def enabled(self)->bool:
        return self._enabled


    @enabled.setter
    def enabled(self, value:bool):
        self._enabled = value


    @property
    def type(self)->str:
        return self._type


    @type.setter
    def type(self, value:str):
        self._type = value


    @property
    def dependencies(self)->list:
        return []


    @dependencies.setter
    def dependencies(self, value:list):
        pass


    @property
    def dependents(self)->list:
        return self._dependents


    @dependents.setter
    def dependents(self, value:list):
        self._dependents = value


    def execute(self):
        logger = Logging.getLogger(self.name)
        logger.info(f"Started Executing {self.__class__.__name__}: {self.name}")
        sleep(5)
        logger.info(f"Finished Executing {self.__class__.__name__}: {self.name}")
        return dict()


    def isReady(self)->bool:
        """work out if it's ok to process. 
        
        This is a blank task node required for workflow
        and doesn't have any dependencies so is always True."""

        return True


    def toDict(self):
        return {
            "name" : self.name ,
            "status" : self.status.name,
            "type" : self.type,
            "enabled" : self.enabled,
            "dependents" : [d.name for d in self.dependents]
        }


    def __str__(self):

        return json.dumps(self.toDict(), indent=4)


