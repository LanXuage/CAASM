#!/bin/env python
from common.module import init_module_from_env

LOGGER_FORMATTER = "%(asctime)s %(levelprefix)s %(message)s"

ACCESS_LOGGER_FORMATTER = (
    '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)

TOKEN_KEY = "6M6cxp4bd3Bx5Cn63Xsnl4yQTMcB5hwR_vpiSx-wWrQ="
TOKEN_TTL = 3000
REDIS_URL = "redis://:redispass@localhost/1"
NEBULA_USERNAME = "root"
NEBULA_PASSWORD = "nebula"
NEBULA_SPACE_NAME = "caasm"
NEBULA_HOST = "localhost"
NEBULA_PORT = "9669"

init_module_from_env(__name__)
