#!/bin/env python
import api

# import aiokafka

from captcha.image import ImageCaptcha
from common.app import App
from common.websocket import WebSocketManager
from common.queue import NotifyQueue, TaskQueue
from common.file import FileManager
from common.log import logger
from common.nebula import NebulaFacade
from contextlib import asynccontextmanager
from cryptography import fernet
from fastapi import status, Request
from fastapi.responses import JSONResponse
from model import resp
from pydantic import RootModel
from redis import asyncio as aioredis
from settings import (
    CAASM_TOKEN_FERNET_KEY,
    CAASM_TOKEN_TTL,
    CAASM_REDIS_URL,
    CAASM_NEBULA_USERNAME,
    CAASM_NEBULA_PASSWORD,
    CAASM_NEBULA_SPACE_NAME,
    CAASM_NEBULA_HOST,
    CAASM_NEBULA_PORT,
    CAASM_TASK_TOPIC_NAME,
    CAASM_KAFKA_BOOTSTRAP_SERVERS,
)


@asynccontextmanager
async def lifespan(app: App):
    logger.info("Initialize token fernet ...")
    app.token_fernet = fernet.Fernet(key=CAASM_TOKEN_FERNET_KEY)
    app.invalid_tokens = set()
    app.token_ttl = CAASM_TOKEN_TTL
    logger.info("Initialize image captcha ...")
    app.image_captcha = ImageCaptcha(width=320, height=120, font_sizes=(62, 70, 76))
    logger.info("Initialize asyncio redis ...")
    app.redis = aioredis.from_url(CAASM_REDIS_URL)
    logger.info("Initialize Nebula facade ...")
    app.nebula_facade = NebulaFacade(
        CAASM_NEBULA_USERNAME,
        CAASM_NEBULA_PASSWORD,
        CAASM_NEBULA_SPACE_NAME,
        [(CAASM_NEBULA_HOST, CAASM_NEBULA_PORT)],
    )
    logger.info("Initialize notify queue ...")
    app.notify_queue = NotifyQueue(CAASM_TASK_TOPIC_NAME, CAASM_KAFKA_BOOTSTRAP_SERVERS)
    await app.notify_queue.start()
    logger.info("Initialize task queue ...")
    app.task_queue = TaskQueue(CAASM_TASK_TOPIC_NAME, CAASM_KAFKA_BOOTSTRAP_SERVERS)
    await app.task_queue.start()
    logger.info("Initialize file manager ...")
    app.file_manager = FileManager()
    logger.info("Initialize websocket manager ...")
    app.websocket_manager = WebSocketManager(app.notify_queue)
    yield
    logger.info("Closing websocket manager ...")
    await app.websocket_manager.close()
    logger.info("Closing file manager ...")
    await app.file_manager.close()
    logger.info("Closing task queue ...")
    await app.task_queue.close()
    logger.info("Closing notify queue ...")
    await app.notify_queue.close()
    logger.info("Closing Nebula facade ...")
    app.nebula_facade.close()
    logger.info("Closing asyncio redis ...")
    await app.redis.close()


app = App(lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exception: Exception):
    if isinstance(exception, fernet.InvalidToken):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=RootModel[resp.Response](
                resp.Response(
                    code=status.HTTP_401_UNAUTHORIZED,
                    data="invalid_token",
                )
            ).model_dump(),
        )
    elif isinstance(exception, AssertionError):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=RootModel[resp.Response](
                resp.Response(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=str(exception)
                )
            ).model_dump(),
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=RootModel[resp.Response](
            resp.Response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data="{}: {}".format(exception.__class__.__name__, exception),
            )
        ).model_dump(),
    )


app.include_router(router=api.v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
