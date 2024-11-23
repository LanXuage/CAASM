#!/bin/env python3

from enum import Enum
from typing import List, Any
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake


class BulkMethod(Enum):
    DELETE = "DELETE"
    POST = "POST"
    PUT = "PUT"


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class Bulk:
    method: BulkMethod
    data: List[Any]
