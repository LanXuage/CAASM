#!/bin/env python
from core.queue import TaskQueue


class Worker:
    def __init__(self, task_topic_name: str, bootstrap_servers: str) -> None:
        self.task_queue = TaskQueue(task_topic_name, bootstrap_servers)

    async def run(self):
        await self.task_queue.start()
        try:
            while True:
                task = await self.task_queue.get()
        except BaseException as e:
            pass
        finally:
            await self.task_queue.close()
