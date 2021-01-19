from .Task import Task, PipelineOrigin
from .Dependency import Dependency
import json
import yaml
from enum import Enum

class DagFormat(Enum):
    # for type safe programming
    OBJECTS = 1
    # python friendly
    DICT = 2
    # HTTP and REST friendly
    JSON = 3
    # human readable
    YAML = 4


class Dag:

    @property
    def name(self)->str:
        return self._name
    

    @name.setter
    def name(self, value:str):
        self._name = value


    def _loadDag(self, projectName:str, pipelines:dict, tasks:dict):

        # create a lookup tasks by task name
        # with dag origin
        taskLookup = {
            self.name : PipelineOrigin("PipelineOrigin", self.name)
        }

        for t in tasks["tasks"]:
            task:Task = Task.taskFactory(t)
            taskLookup[task.name] = task

        # create a lookup of tasks by group name
        # we need this to easily add dependecies
        taskGroupLookup = {projectName: []}
        groupKeys = [projectName]
        if pipelines and pipelines["pipelines"]:
            self._indexTaskGroups(groupKeys, pipelines["pipelines"], taskLookup, taskGroupLookup)

        # create the dag and an origin task
        self.dag = dict()
        self.dag[self.name] = taskLookup[self.name]

        # if has pipelines then recurse them for tasks
        if pipelines and pipelines["pipelines"]:
            self._addTasks(pipelines["pipelines"], taskLookup, taskGroupLookup, self.dag)


    def _addTasksToGroupLkp(self, taskName:str, groupKeys:list, tasks:dict, taskGroupLookup:dict):

        for k in groupKeys:
            try:
                if not tasks[taskName] in taskGroupLookup[k]:
                    taskGroupLookup[k].append(tasks[taskName])
            except KeyError:
                # the tasks isn't in the tasks lookup
                # ocam's razor, if it's not in the lookup then 
                # it's not in the tasks definition yaml file.
                raise Exception(f"Tasks {taskName} is not found in the task definitions.")


    def _indexTaskGroups(self, groupKeys:list, pipelineTasks:dict, tasks:dict, taskGroupLookup:dict):

        for t in pipelineTasks:
            # these are tasks, add them to group key
            # but only is they already haven't been added to a parent on
            # a previous iteration.
            if type(t) is str:
                self._addTasksToGroupLkp(t, groupKeys, tasks, taskGroupLookup)

            # these are groups
            # create a groupkey and them to the keys list used to add child tasks
            elif t.get("name") and t.get("tasks"):
                # fork the group keys
                nextGroupKeys = groupKeys[:]
                # create a new key and empty lists to append tasks
                nextGroupKeys.append(t.get("name"))
                taskGroupLookup[t.get("name")] = []
                # we're in a task group so we need to recurse down to find tasks.
                self._indexTaskGroups(nextGroupKeys, t["tasks"], tasks, taskGroupLookup)

            # if it's neither we have a problem huston!
            # yaml's will be validated when loaded so this shouldn't happen
            # but stranger things have happened!
            else:
                raise Exception("Unexpected malformed pipeline. DAG nodes must be a task group with a tasks list or a task name as string.")


    def _getTaskEnabled(self, task:dict, enabled:bool):

        if task.get("enabled"):
            return t["enabled"]=="True"
        else:
            return enabled 


    def _addTasksToDag(self, taskName:str, tasks:dict, dag:dict, dependencies:list, enabled:bool):

        try:
            
            # add the properties and dependencies to the tasks
            tasks[taskName].enabled = enabled

            if len(dependencies) == 0:
                tasks[taskName].dependencies = [Dependency(tasks[self.name])]
            else:
                tasks[taskName].dependencies = dependencies

            # add the task to the dag dictionary
            dag[taskName] = tasks[taskName]

            # add the task the dependents list of the tasks in the dependents list
            # i.e add the top down traversal task dependency relationship 
            for d in tasks[taskName].dependencies:
                task = d.task
                task.dependents.append(tasks[taskName])

        except KeyError:

            # the tasks isn't in the tasks lookup
            # ocam's razor, if it's not in the lookup then 
            # it's not in the tasks definition yaml file.
            raise Exception(f"Tasks {taskName} is not found in the task definitions.") 


    def _getDependencies(self, task:dict, tasks:dict, taskGroups:dict, dependencies:list):
        grpDependencies:list = None
        if task.get("dependsOn"):

            # for each dependency add the task object
            # or the group of tasks objects to the dependcy list
            grpDependencies = dependencies[:]
            for d in task["dependsOn"]:
                # if it's a task just add the task, replacing the name
                if tasks.get(d["task"]):                            
                    grpDependencies.append(Dependency(tasks[d["task"]], d["condition"], d["operator"]))
                
                # if it's a group of tasks add all the tasks using the
                # taskGroup index of tasks
                if taskGroups.get(d["task"]):
                    for g in taskGroups[d["task"]]:
                        grpDependencies.append(Dependency(g, d["condition"], d["operator"]))

        return grpDependencies


    def _addTasks(self, pipelineTasks:dict, tasks:dict, taskGroups:dict, dag:dict, dependencies:list=None, enabled:bool=True):

        if not dependencies:
            dependencies = list()

        # looks for tasks in the pipeline DAG
        for t in pipelineTasks:
            # if it's a task add it to the dag
            if type(t) is str:
                self._addTasksToDag(t, tasks, dag, dependencies, enabled)

            # if it's a task group recurse down to look for tasks
            elif t["tasks"]:
                # look to see if the task group has an enabled attribtue
                # if it has pass it down.
                tasksEnabled = self._getTaskEnabled(t, enabled)

                # look to see of the task has any dependencies
                # if so add them to any parent dependencies and pass it down
                # note that we copy the list because we iterating task groups
                # we only want to pass the parent group dependencies down 
                # not the previous sibling
                grpDependencies:list = self._getDependencies(t, tasks, taskGroups, dependencies)

                # recurse down the hierarchy of task groups passing down the
                # dependencies and enabled state.
                self._addTasks(t["tasks"], tasks, taskGroups, dag, grpDependencies, tasksEnabled)

            # if it's neither we have a problem huston!
            # yaml's will be validated when loaded so this shouldn't happen
            # but stranger things have happened!
            else:
                raise Exception("Unexpected malformed pipeline. DAG nodes must be a task group with a tasks list or a task name as string.")


    def _getDagDict(self, dag:dict):
        tod = dict()
        for k, v in dag.items():
            if isinstance(v, dict):
                tod[k] = self._getDagDict(v)
            elif isinstance(v, Task):
                tod[k] = v.toDict()
            elif isinstance(v, list):
                tod[k] = [i.task.name for i in v]
        return tod


    def getDag(self, format:DagFormat=DagFormat.OBJECTS, indent:int=4):

        if(format == DagFormat.OBJECTS):
            return self.dag
        elif(format == DagFormat.DICT):
            return self._getDagDict(self.dag)
        elif(format == DagFormat.JSON):
            return json.dumps(self._getDagDict(self.dag), indent=indent)
        elif(format == DagFormat.YAML):
            return yaml.dump(self._getDagDict(self.dag), indent=indent)


    def getDagOrigin(self):

        return self.dag[self.name]
