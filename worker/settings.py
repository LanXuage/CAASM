#!/bin/env python
from core.module import init_module_from_env

CAASM_TASK_TOPIC_NAME = "task"
CAASM_KAFKA_BOOTSTRAP_SERVERS = "queue:9092"

init_module_from_env(__name__)
