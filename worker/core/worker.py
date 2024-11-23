#!/bin/env python
from .nebula import NebulaFacade
from .queue import TaskQueue
from .log import logger
from typing import List, Tuple, Union


class Worker:
    def __init__(
        self,
        task_topic_name: str,
        bootstrap_servers: str,
        username: str,
        password: str,
        space_name: str,
        addresses: List[Tuple[str, Union[int, str]]],
    ) -> None:
        self.task_queue = TaskQueue(task_topic_name, bootstrap_servers)
        self.nebula_facade = NebulaFacade(username, password, space_name, addresses)

    async def run(self):
        logger.info("Worker running...")
        await self.task_queue.start()
        while True:
            try:
                task = await self.task_queue.get()
                logger.info("task %s", task)
                await task.run(self.nebula_facade)
            except BaseException as e:
                logger.warning("run error", exc_info=e)

    async def close(self):
        await self.task_queue.close()
