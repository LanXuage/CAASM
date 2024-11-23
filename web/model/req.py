#!/bin/env python
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
class LoginRequest:
    username: str
    password: str
    captcha: str
    s: str
