#!/bin/env python
import msgpack

from aiokafka import AIOKafkaConsumer
from .model import Task
from typing import Any


class AbstractQueue:
    def __init__(self, topic_name: str, bootstrap_servers: str) -> None:
        self.consumer = AIOKafkaConsumer(
            topic_name, bootstrap_servers=bootstrap_servers
        )
        self.topic_name = topic_name

    async def start(self):
        await self.consumer.start()

    async def put(self, msg: Any):
        raise NotImplementedError

    async def get(self) -> Any:
        raise NotImplementedError

    async def close(self):
        await self.consumer.stop()


class TaskQueue(AbstractQueue):
    async def put(self, task: Task):
        raise NotImplementedError

    async def get(self) -> Task:
        msg = await anext(self.consumer)
        return msgpack.unpackb(msg.value)
