#!/bin/env python3
import asyncio

from core.worker import Worker
from settings import CAASM_KAFKA_BOOTSTRAP_SERVERS, CAASM_TASK_TOPIC_NAME

if __name__ == "__main__":
    worker = Worker(CAASM_TASK_TOPIC_NAME, CAASM_KAFKA_BOOTSTRAP_SERVERS)
    asyncio.run(worker.run())
