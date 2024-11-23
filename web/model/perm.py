#!/bin/env python3

from common.datetime import ZONE_INFO
from datetime import datetime
from typing import List
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator, Field
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
class Perm:
    id: str
    perm_name: str
    perm_desc: str
    updated_at: datetime = datetime.now(tz=ZONE_INFO)
    created_at: datetime = datetime.now(tz=ZONE_INFO)
    submenus: List["Perm"] = Field(default_factory=lambda: [])
