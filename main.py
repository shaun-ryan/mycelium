# from fathom.ConnectStorage import ConnectStorage
# ConnectStorage()

from mycelium.Project import Project
from mycelium.Dag import DagFormat

project = Project("./pipelineProjects/")
# print(project.getDag(DagFormat.DICT))

with open("./taskDag.yaml", "w") as f:
    f.writelines(project.getDag(DagFormat.YAML))

with open("./taskDag.json", "w") as f:
    f.writelines(project.getDag(DagFormat.JSON))

project.execute()


# from mycelium import Logging

# logger = Logging.getLogger("./pipelineProjects/", __name__)





