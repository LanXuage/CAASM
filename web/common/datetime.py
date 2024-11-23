#!/bin/env python
from os import environ

from zoneinfo import ZoneInfo

ZONE_INFO = ZoneInfo(environ.get("TZ") or "Asia/Shanghai")
