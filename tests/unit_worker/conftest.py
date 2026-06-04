#!/bin/env python3
"""
Worker test configuration - sets up worker/ in sys.path.
Isolated from web tests to avoid import conflicts.
"""
import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_WORKER_PATH = os.path.join(_PROJECT_ROOT, "worker")

# Add worker/ before other paths so worker imports resolve correctly
sys.path.insert(0, _WORKER_PATH)
sys.path.insert(0, _PROJECT_ROOT)