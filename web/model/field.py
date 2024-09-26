#!/bin/env python3
import pydantic

from datetime import datetime
from typing import List, Optional
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
class Field:
    field_name: str
    field_desc: str
    id: Optional[str] = None
    updated_at: datetime = datetime.now()
    created_at: datetime = datetime.now()
    collects: List[str] = pydantic.Field(default_factory=lambda: [])
