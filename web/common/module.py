#!/bin/env python
import sys

from os import environ


def init_module_from_env(module_name: str):
    module = sys.modules[module_name]
    for var_key in dir(module):
        if not var_key.startswith("CAASM_"):
            continue
        var_value = environ.get(var_key)
        if var_value is not None:
            module.__setattr__(var_key, var_value)
