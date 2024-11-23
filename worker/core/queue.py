#!/bin/env python
import msgpack

from abc import ABC, abstractmethod
from aiokafka import AIOKafkaConsumer
from .task import Task, TaskType, BulkTask
from typing import Any


class AbstractQueue(ABC):
    def __init__(self, topic_name: str, bootstrap_servers: str) -> None:
        self.consumer = AIOKafkaConsumer(
            topic_name, bootstrap_servers=bootstrap_servers
        )
        self.topic_name = topic_name

    async def start(self):
        await self.consumer.start()

    @abstractmethod
    async def put(self, msg: Any):
        raise NotImplementedError

    @abstractmethod
    async def get(self) -> Any:
        raise NotImplementedError

    async def close(self):
        await self.consumer.stop()


class TaskQueue(AbstractQueue):
    async def put(self, task: Task):
        raise NotImplementedError

    async def get(self) -> Task:
        msg = await anext(self.consumer)
        task = msgpack.unpackb(msg.value, timestamp=3)
        if task.get("task_type") == TaskType.BULK.value:
            return BulkTask(**task)
        else:
            raise Exception("Unspport task type")
