#!/bin/env python3
"""
Unit tests for shared.module:
- init_module_from_env()
"""

import sys
import pytest
from unittest.mock import patch
from types import ModuleType

from shared.module import init_module_from_env


@pytest.fixture
def test_module():
    """Create a test module with CAASM_ prefixed variables."""
    mod = ModuleType("test_module")
    mod.CAASM_TEST_VAR = "default_value"
    mod.CAASM_OTHER_VAR = 42
    mod.NON_CAASM_VAR = "should_not_change"
    sys.modules["test_module"] = mod
    yield mod
    del sys.modules["test_module"]


def test_init_module_overwrites_with_env_var(test_module):
    """CAASM_ prefixed variables should be overwritten by env vars."""
    with patch.dict("os.environ", {"CAASM_TEST_VAR": "from_env"}):
        init_module_from_env("test_module")

    assert test_module.CAASM_TEST_VAR == "from_env"


def test_init_module_keeps_default_without_env(test_module):
    """Without corresponding env var, default should be kept."""
    init_module_from_env("test_module")

    assert test_module.CAASM_TEST_VAR == "default_value"
    assert test_module.CAASM_OTHER_VAR == 42


def test_init_module_does_not_touch_non_caasm(test_module):
    """Non-CAASM_ prefixed variables should not be affected."""
    with patch.dict("os.environ", {"NON_CAASM_VAR": "changed"}):
        init_module_from_env("test_module")

    assert test_module.NON_CAASM_VAR == "should_not_change"


def test_init_module_partial_overwrite(test_module):
    """Only matching env vars should overwrite."""
    with patch.dict("os.environ", {"CAASM_TEST_VAR": "new_value"}):
        init_module_from_env("test_module")

    assert test_module.CAASM_TEST_VAR == "new_value"
    assert test_module.CAASM_OTHER_VAR == 42  # unchanged


def test_init_module_nonexistent_var():
    """Module without any CAASM_ vars should not raise error."""
    mod = ModuleType("empty_module")
    sys.modules["empty_module"] = mod
    try:
        init_module_from_env("empty_module")
    finally:
        del sys.modules["empty_module"]