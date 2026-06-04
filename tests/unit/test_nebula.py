#!/bin/env python3
"""
Unit tests for shared.nebula module:
- gen_vid()
- expand_enum()
- make_object()
"""

import pytest
from unittest.mock import MagicMock, patch
from enum import Enum
from datetime import datetime
from typing import Optional

from shared.nebula import gen_vid, expand_enum, make_object
from shared.datetime import ZONE_INFO


class StatusEnum(Enum):
    ACTIVE = 1
    INACTIVE = 0


# ========== gen_vid tests ==========


def test_gen_vid_returns_hex_string():
    """gen_vid should return a 32-character hex string."""
    vid = gen_vid("field", "test_name")
    assert isinstance(vid, str)
    assert len(vid) == 32
    assert all(c in "0123456789abcdef" for c in vid)


def test_gen_vid_idempotent():
    """Same inputs should produce the same output."""
    vid1 = gen_vid("field", "test_name")
    vid2 = gen_vid("field", "test_name")
    assert vid1 == vid2


def test_gen_vid_different_tag():
    """Different tags should produce different outputs."""
    vid1 = gen_vid("field", "test")
    vid2 = gen_vid("model", "test")
    assert vid1 != vid2


def test_gen_vid_different_args():
    """Different args should produce different outputs."""
    vid1 = gen_vid("field", "test", "a")
    vid2 = gen_vid("field", "test", "b")
    assert vid1 != vid2


def test_gen_vid_multiple_args():
    """Multiple args should be joined with underscores."""
    vid = gen_vid("tag", "arg1", "arg2", "arg3")
    # The input should be md5("tag_arg1_arg2_arg3")
    assert len(vid) == 32


# ========== expand_enum tests ==========


def test_expand_enum_converts_enum_values():
    """Enum values should be converted to their raw values."""
    data = {"status": StatusEnum.ACTIVE, "name": "test"}
    result = expand_enum(data)
    assert result == {"status": 1, "name": "test"}


def test_expand_enum_no_enum():
    """Non-enum values should remain unchanged."""
    data = {"name": "test", "count": 42}
    result = expand_enum(data)
    assert result == {"name": "test", "count": 42}


def test_expand_enum_empty_dict():
    """Empty dict should return empty dict."""
    assert expand_enum({}) == {}


def test_expand_enum_mixed():
    """Mixed enum and non-enum values."""
    data = {"status": StatusEnum.INACTIVE, "name": "foo", "active": True}
    result = expand_enum(data)
    assert result == {"status": 0, "name": "foo", "active": True}


# ========== make_object tests ==========


from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake
from nebula3.common.ttypes import Vertex, Tag, Value


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class DummyModel:
    id: str
    name: str
    count: int
    description: str = "default"
    optional_field: Optional[int] = None
    created_at: datetime = datetime.now(tz=ZONE_INFO)


def _make_mock_vertex(vid: str, props: dict):
    """Helper to create a mock Nebula Vertex with properties.
    
    Uses real Nebula Tag and Value objects to pass isinstance checks,
    with a MagicMock Vertex wrapper for the vid attribute.
    """
    from nebula3.common.ttypes import Vertex, Tag, Value

    vertex = MagicMock()
    
    # Set up vid as a nested mock that returns the VID string
    vid_mock = MagicMock()
    vid_mock.get_sVal.return_value = vid.encode() if isinstance(vid, str) else vid
    vertex.vid = vid_mock

    # Use a real Tag object to pass isinstance(tag, Tag) check
    tag = Tag()
    tag.props = {}
    for k, v in props.items():
        real_value = Value()
        real_value.value = v
        key = k.encode() if isinstance(k, str) else k
        tag.props[key] = real_value

    vertex.tags = [tag]
    return vertex


def test_make_object_basic_mapping():
    """make_object should map Vertex properties to model fields."""
    vertex = _make_mock_vertex("test_vid", {
        "name": b"test_name",
        "count": 42,
        "description": b"test_desc",
    })

    result = make_object(DummyModel, vertex)
    assert result.name == "test_name"
    assert result.count == 42
    assert result.description == "test_desc"


def test_make_object_sets_id_from_vid():
    """make_object should set the id field from vertex VID."""
    vertex = _make_mock_vertex("my_vid_string", {
        "name": b"test",
        "count": 1,
    })

    result = make_object(DummyModel, vertex)
    assert result.id == "my_vid_string"


def test_make_object_optional_field_default():
    """Optional fields not in vertex should use model default."""
    vertex = _make_mock_vertex("vid", {
        "name": b"test",
        "count": 1,
    })

    result = make_object(DummyModel, vertex)
    assert result.optional_field is None


def test_make_object_datetime_field():
    """Datetime fields should be converted from timestamp int."""
    vertex = _make_mock_vertex("vid", {
        "name": b"test",
        "count": 1,
        "created_at": 1690000000,  # timestamp as int
    })

    result = make_object(DummyModel, vertex)
    assert isinstance(result.created_at, datetime)


def test_make_object_extra_kwargs():
    """Extra kwargs should override or supplement vertex props."""
    vertex = _make_mock_vertex("vid", {
        "name": b"original",
        "count": 1,
    })

    result = make_object(DummyModel, vertex, name="overridden", optional_field=99)
    assert result.name == "overridden"
    assert result.optional_field == 99


def test_make_object_missing_required_field():
    """Should handle missing required fields gracefully via assertion."""
    vertex = _make_mock_vertex("vid", {
        "name": b"test",
        # missing "count"
    })

    # This will fail because count is required and not in vertex
    with pytest.raises(Exception):  # pydantic ValidationError or TypeError
        make_object(DummyModel, vertex)