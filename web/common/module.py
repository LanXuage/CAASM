#!/bin/env python3
# Re-export from shared package to maintain backward compatibility.
# New code should import directly from shared.module.
from shared.module import init_module_from_env  # noqa: F401