import logging
import logging.config
import yaml
import os


def getLogger(name:str)->logging:

    directoryPath = os.getenv("MYCELIUMPROJECTSDIR")
    with open(f"{directoryPath}logging.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    return logging.getLogger(name)

