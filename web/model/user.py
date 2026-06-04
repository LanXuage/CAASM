#!/bin/env python3

from common.datetime import ZONE_INFO
from datetime import datetime
from typing import Optional, List
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
class User:
    id: str
    username: str
    real_name: str
    phone: str
    email: str
    user_status: int
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
class UserDetail(User):
    """User with role information."""
    roles: List[str] = Field(default_factory=lambda: [])


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class UserCreate:
    """Request model for creating a user."""
    username: str
    password: str
    real_name: str = ""
    phone: str = ""
    email: str = ""
    user_status: int = 1


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class UserUpdate:
    """Request model for updating a user."""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    user_status: Optional[int] = None


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class UserStatusChange:
    """Request model for changing user status."""
    user_status: int


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class UserAssignRoles:
    """Request model for assigning roles to a user."""
    role_ids: List[str]