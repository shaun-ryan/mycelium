
import os
import yaml
import threading
from typing import List
from .Task import Task, DatabricksNotebook, TaskStatus, PipelineOrigin
from .Dag import Dag 
from .Worker import Worker
from . import Logging


class Project(Dag, Task, Worker):


    def __init__(self, directoryPath:str=None):
        """Initialise the project.

        Load the project.yaml file  using the direcoty parameter or PIPELINEPROJECTSDIR environment variable.
        Load the yaml project files into dictionaries.
        """

        # setup the path envirionemnt variable for project dir and logging
        self.directory = os.getenv("MYCELIUMPROJECTSDIR")
        if directoryPath:
            self.directory = directoryPath
        os.environ["MYCELIUMPROJECTSDIR"] = self.directory
        logger = Logging.getLogger(__name__)

        Worker.__init__(self)
        self.status = TaskStatus.NONE
        self.enabled = True
        self.name = None
        self.maxParallel = 4
        self.type = self.__class__.__name__
        self._pipelineFiles:List = None
        self._taskFiles:List = None
        self._patternFiles:List = None
        self._dag:List = None
        self.projectFilePath = os.path.join(self.directory, "mycelium.yaml")
        logger.info(f"Loading Mycelium Project: {self.projectFilePath}")

        with open(self.projectFilePath, 'r') as f:

            projectDict = yaml.safe_load(f)
            self._load(**projectDict["project"])


    @property
    def status(self)->TaskStatus:
        return self._status


    @status.setter
    def status(self, value:TaskStatus):
        self._status = value


    @property
    def name(self)->str:
        return super().name


    @name.setter
    def name(self, value:str):
        super(Project, self.__class__).name.fset(self, value)


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
        pass


    @dependencies.setter
    def dependencies(self, value:list):
        pass


    @property
    def dependents(self)->list:
        pass


    @dependents.setter
    def dependents(self, value:list):
        pass


    def _load(self,
                name: str,
                directory: str,
                pipelines: List[str],
                tasks: List[str],
                patterns: List[str]):
        """Load the project yaml files into a task dictionary and a pipeline dictionary."""

        TASKS_KEY = "tasks"
        PATTERNS_KEY = "patterns"
        PIPELINES_KEY = "pipelines"

        pipelineDict:dict = None
        taskDict:dict = None
        patternDict:dict = None

        self.name = name
        self.directory = os.path.join(self.directory, directory).replace("/./", "/")
        self._pipelineFiles = pipelines
        self._taskFiles = tasks
        self._patternFiless = patterns

        # Load and merge pipeline yaml files into a single dictionary
        pipelineDict = [
            self._loadYaml(self.directory + i, pipelineDict, PIPELINES_KEY) 
            for i in self._pipelineFiles][0]
        self.maxParallel = pipelineDict["maxParallel"]

        # Load and merge tasks yaml files into a single dictionary
        taskDict = [
            self._loadYaml(self.directory + i, taskDict, TASKS_KEY) 
            for i in self._taskFiles][0]
        

        # Load and merge patterns yaml files into a single dictionary
        patternDict = [
            self._loadYaml(self.directory + i, patternDict, PATTERNS_KEY) 
            for i in self._patternFiless][0]
    
        # Fill missing task properties with their pattern attributes
        # where patterns have been declared.
        # Note that if required attribute it missing from the task it's self or any declared pattern
        # then it will fail validation.
        self._stitchTaskPatterns(taskDict[TASKS_KEY], patternDict[PATTERNS_KEY])
        
        # build a task dag, this is dictionary tasks, each task has a list of depends on tasks.
        self._loadDag(self.name, pipelineDict, taskDict)


    def _find(self, dictionary:dict, name:str):
        """Find a dictionary item by name."""

        found = next(i for i in dictionary if i["name"].lower() == name.lower())
        return found


    def _stitchTaskPatterns(self, tasks:dict, patterns:dict):
        """Fill attributes into tasks from patterns where they have a pattern attribute.

        Patterns allow for re-use. Many tasks have the same parameters and it's useful to 
        re-use dictionary object of key value pairs instead of users having to type out
        the same attributes everytime. These are declared in the patterns files. The tasks
        can then reference a pattern using a pattern attribute. When a pattern attribute references
        a pattern name the it must uniquely exist in the patterns files and the attributes are taken
        from the pattern where the task does not have them. In otherwords the task may override a
        subset of the of pattern attributes (thus partially using a pattern) if desired for more flexibility.
        """

        PATTERN_KEY = "pattern"
        for task in tasks:
            if task[PATTERN_KEY]:
                pattern = self._find(patterns, task[PATTERN_KEY])
                for k, v in pattern.items():
                    if not k in task.keys():
                        task[k] = v 
                del task[PATTERN_KEY]


    def _loadYaml(self, path:str, collection:dict, collectKey:str):
        """Loads the collection yaml file into a dictionary.

        Loads the collection yaml file version=sibytes.io/mycelium/[collection]/api/0.1.0
        into a dictionary and merges the collection item lists into the objects existing dictionary
        of objects. If this does not exist yet it will be created. The function returns the resulting
        dictionary
        """
        logger = Logging.getLogger(self.name)
        logger.info(f"Loading {path}...")

        with open(path) as f:
            newCollection = yaml.safe_load(f)

            if collection:
                collection[collectKey] = [*collection[collectKey], *newCollection[collectKey]]
            else:
                collection = newCollection

        return collection


    def execute(self, maxParallel:int=0)->dict:

        logger = Logging.getLogger(self.name)

        # override max parallel if provided
        if maxParallel > 0:
            self.maxParallel = maxParallel


        if self.isReady():
            logger.info(f"Starting thread pool with maxParallel with maxParallel={self.maxParallel}")
            for i in range(self.maxParallel):
                threading.Thread(target=self._worker, daemon=True).start()

            logger.info(f"Starting executing project={self.name}")
            self._queue.put(self.getDagOrigin())

            self._queue.join()

            logger.info(f"Finished executing project={self.name}")

        else:
            logger.info(f"Failed to start project {self.name}, it is not ready.")

        result = dict()

        return result


    def isReady(self)->bool:
        """Check that the project DAG isn't processing

        If nothing has been processed yet all the task status will be NONE.
        """

        # override max parallel if provided
        unprocessedTasks = [t for t in self.dag if self.dag[t].status == TaskStatus.NONE]

        return len(unprocessedTasks) == len(self.dag)

