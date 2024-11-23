#!/bin/env python3

from common.datetime import ZONE_INFO
from datetime import datetime
from enum import Enum
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake
from typing import List, Union, Any, Optional
from .bulk import BulkMethod


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
