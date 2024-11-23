#!/bin/env python3
import msgpack

from abc import ABC, abstractmethod
from aiokafka import AIOKafkaProducer
from pydantic import RootModel
from common.log import logger
from model import Task
from typing import Any
from .nebula import expand_enum


class AbstractQueue(ABC):
    def __init__(self, topic_name: str, bootstrap_servers: str) -> None:
        self.producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
        self.topic_name = topic_name

    async def start(self):
        await self.producer.start()

    @abstractmethod
    async def put(self, msg: Any):
        raise NotImplementedError

    @abstractmethod
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
        data = RootModel[task.__class__](task).model_dump()
        logger.info("task model dump %s", data)
        await self.producer.send_and_wait(
            self.topic_name, msgpack.packb(expand_enum(data), datetime=True)
        )

    async def get(self) -> Task:
        raise NotImplementedError
