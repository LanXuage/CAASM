#!/bin/env python3
# Re-export from shared.models for backward compatibility.
# Web-side models: pure data definitions, no run() logic.
from shared.models.task import (  # noqa: F401
    TaskType,
    TaskStatus,
    BulkMethod,
    Task,
    BulkTask,
)