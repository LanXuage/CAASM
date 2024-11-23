#!/bin/env python3
import os

from enum import Enum
from .log import logger
from abc import abstractmethod
from .nebula import NebulaFacade
from datetime import datetime
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake
from typing import List, Any, Optional
from settings import CAASM_WATER_LINE
from .datetime import ZONE_INFO


class BulkMethod(Enum):
    DELETE = "DELETE"
    POST = "POST"
    PUT = "PUT"


class TaskType(Enum):
    BULK = 0


class TaskStatus(Enum):
    QUEUING = 0
    RUNNING = 1
    ABNORMAL = 2
    END = 3


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class Task:
    id: str
    task_type: TaskType
    task_status: TaskStatus
    started_at: datetime = datetime.fromtimestamp(0, tz=ZONE_INFO)
    ended_at: datetime = datetime.fromtimestamp(0, tz=ZONE_INFO)
    updated_at: datetime = datetime.now(tz=ZONE_INFO)
    created_at: datetime = datetime.now(tz=ZONE_INFO)

    @abstractmethod
    async def run(self):
        raise NotImplementedError


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class BulkTask(Task):
    tag: Optional[str] = None
    method: Optional[BulkMethod] = None
    data: Optional[List[Any]] = None

    async def run(self, nebula_facade: NebulaFacade):
        logger.info("Run bulk task...")
        if self.method == BulkMethod.DELETE:
            if len(self.data) < CAASM_WATER_LINE:
                logger.info("Data size less than %s(water line)")
                stmt = 'DELETE VERTEX "'
                for vid in self.data:
                    stmt += '{}","'.format(vid)
                stmt = stmt[:-2] + " WITH EDGE"
                logger.info("Delete nGQL %s", stmt)
                result = nebula_facade.execute(stmt)
                assert result.is_succeeded(), "Execute nGQL failed"
            else:
                logger.info("Data size more than %s(water line)")
        elif self.method == BulkMethod.POST:
            logger.info("post")
        elif self.method == BulkMethod.PUT:
            logger.info("put")
        else:
            raise Exception("Unspport bulk method")
