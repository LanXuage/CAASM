#!/bin/env python
from common.module import init_module_from_env

CAASM_LOGGER_FORMATTER = "%(asctime)s %(levelprefix)s %(message)s"

CAASM_ACCESS_LOGGER_FORMATTER = (
    '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)

CAASM_TOKEN_FERNET_KEY = "6M6cxp4bd3Bx5Cn63Xsnl4yQTMcB5hwR_vpiSx-wWrQ="
CAASM_TOKEN_KEY = "X-Token"
CAASM_TOKEN_TTL = 3000
CAASM_REDIS_URL = "redis://:redispass@localhost/1"
CAASM_NEBULA_USERNAME = "root"
CAASM_NEBULA_PASSWORD = "nebula"
CAASM_NEBULA_SPACE_NAME = "caasm"
CAASM_NEBULA_HOST = "localhost"
CAASM_NEBULA_PORT = "9669"

init_module_from_env(__name__)
