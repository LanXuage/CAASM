#!/bin/env python
from pydantic.dataclasses import dataclass


@dataclass
class LoginRequest:
    username: str
    password: str
    captcha: str
    s: str
