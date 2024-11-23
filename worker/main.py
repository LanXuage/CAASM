#!/bin/env python3
import asyncio

from core.worker import Worker
from settings import (
    CAASM_KAFKA_BOOTSTRAP_SERVERS,
    CAASM_TASK_TOPIC_NAME,
    CAASM_NEBULA_HOST,
    CAASM_NEBULA_PASSWORD,
    CAASM_NEBULA_PORT,
    CAASM_NEBULA_SPACE_NAME,
    CAASM_NEBULA_USERNAME,
)


async def main():
    worker = Worker(
        CAASM_TASK_TOPIC_NAME,
        CAASM_KAFKA_BOOTSTRAP_SERVERS,
        CAASM_NEBULA_USERNAME,
        CAASM_NEBULA_PASSWORD,
        CAASM_NEBULA_SPACE_NAME,
        [(CAASM_NEBULA_HOST, CAASM_NEBULA_PORT)],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
