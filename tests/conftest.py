#!/bin/env python3
"""
Global test fixtures and configuration.

With uv workspace, shared/ is installed as a package and always importable.
web/ is a virtual project - its modules (common, model, api, deps) need
web/ in the Python path for 'from common.nebula import ...' style imports.
"""

import sys
import os

# Add web/ to path so web test modules can import from common, model, api, deps
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "web"))

import pytest
import logging

# Suppress excessive logging during tests
logging.basicConfig(level=logging.WARNING)
logging.getLogger("shared.nebula").setLevel(logging.WARNING)


@pytest.fixture
def sample_vertex_data():
    """Provide sample vertex property data for make_object tests."""
    return {
        "username": b"admin",
        "passwd": b"admin",
        "real_name": b"Administrator",
        "phone": b"1234567890",
        "email": b"admin@example.com",
        "user_status": 1,
    }