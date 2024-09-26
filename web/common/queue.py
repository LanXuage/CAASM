#!/bin/env python3
import msgpack

from aiokafka import AIOKafkaProducer
from model import Task
from typing import Any


class AbstractQueue:
    def __init__(self, topic_name: str, bootstrap_servers: str) -> None:
        self.producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
        self.topic_name = topic_name

    async def start(self):
        await self.producer.start()

    async def put(self, msg: Any):
        raise NotImplementedError

    async def get(self) -> Any:
        raise NotImplementedError

    async def close(self):
        await self.producer.stop()


class Notify:
    pass


class NotifyQueue(AbstractQueue):
    async def put(self, notify: Notify):
        pass

    async def get(self) -> Notify:
        return Notify()


class TaskQueue(AbstractQueue):
    async def put(self, task: Task):
        await self.producer.send_and_wait(self.topic_name, msgpack.packb(task))

    async def get(self) -> Task:
        raise NotImplementedError
