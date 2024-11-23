#!/bin/env python
from core.module import init_module_from_env

CAASM_LOGGER_FORMATTER = "%(asctime)s %(levelprefix)s %(message)s"

CAASM_ACCESS_LOGGER_FORMATTER = (
    '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
)
CAASM_NEBULA_USERNAME = "root"
CAASM_NEBULA_PASSWORD = "nebula"
CAASM_NEBULA_SPACE_NAME = "caasm"
CAASM_NEBULA_HOST = "graphd"
CAASM_NEBULA_PORT = "9669"
CAASM_WATER_LINE = 1000
CAASM_TASK_TOPIC_NAME = "task"
CAASM_KAFKA_BOOTSTRAP_SERVERS = "queue:9092"

init_module_from_env(__name__)
