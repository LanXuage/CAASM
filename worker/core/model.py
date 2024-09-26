#!/bin/env python3

from datetime import datetime
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake


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
    task_type: int
    task_status: int
    started_at: datetime = datetime.fromtimestamp(0)
    ended_at: datetime = datetime.fromtimestamp(0)
    updated_at: datetime = datetime.now()
    created_at: datetime = datetime.now()