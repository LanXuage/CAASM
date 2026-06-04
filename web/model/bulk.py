#!/bin/env python3
# Re-export BulkMethod from shared.models for backward compatibility.
from shared.models.task import BulkMethod  # noqa: F401

from enum import Enum
from typing import List, Any
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
class Bulk:
    method: BulkMethod
    data: List[Any]