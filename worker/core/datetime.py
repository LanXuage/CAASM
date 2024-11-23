#!/bin/env python
import os

from zoneinfo import ZoneInfo

ZONE_INFO = ZoneInfo(os.environ.get("TZ") or "Asia/Shanghai")
