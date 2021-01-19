import threading
from queue import Queue
import time
import uuid
from .Task import Task, TaskStatus
from . import Logging
import os
import uuid


class Worker:

    def __init__(self):

        self._queue = Queue()
        self._lock = threading.Lock()


    def _worker(self):

        while True:

            tname = threading.currentThread()._name + "_" + str(uuid.uuid4())
            logger = Logging.getLogger(tname)

            task:Task = self._queue.get()
            logger.debug(f"Trying: {task.name}")

            # needs to be locked because we're reading the status
            # of the task that may already be processing.
            with self._lock:
                isReady = task.isReady()

            if isReady:

                if task.enabled:
                    result = task.execute()

                else:
                    logger.info(f"Skipping disabled task: {task}")

                for t in task.dependents:

                    # don't need to lock it because no threads
                    # can interact with it until it's on the queue by convention
                    # if this changes then it needs to be locked.
                    with self._lock:
                        t.status = TaskStatus.QUEUED
                    
                    self._queue.put(t)

            else:
                logger.debug(f"Task not ready: {task.name}")

            self._queue.task_done()

