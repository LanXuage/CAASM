#!/bin/env python3

from common.datetime import ZONE_INFO
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
class User:
    id: str
    username: str
    real_name: str
    phone: str
    email: str
    user_status: int
    updated_at: datetime = datetime.now(tz=ZONE_INFO)
    created_at: datetime = datetime.now(tz=ZONE_INFO)
