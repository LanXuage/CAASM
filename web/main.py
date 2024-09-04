#!/bin/env python
import api

from model import resp
from common.app import App
from common.log import logger
from pydantic import RootModel
from cryptography import fernet
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import Request, status
from fastapi.responses import JSONResponse
from captcha.image import ImageCaptcha
from nebula3.Config import SessionPoolConfig
from nebula3.gclient.net.SessionPool import SessionPool
from settings import (
    CAASM_TOKEN_FERNET_KEY,
    CAASM_TOKEN_TTL,
    CAASM_REDIS_URL,
    CAASM_NEBULA_USERNAME,
    CAASM_NEBULA_PASSWORD,
    CAASM_NEBULA_SPACE_NAME,
    CAASM_NEBULA_HOST,
    CAASM_NEBULA_PORT,
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
    logger.info("Initialize Nebula session pool ...")
    app.nebula_sess_pool = SessionPool(
        CAASM_NEBULA_USERNAME,
        CAASM_NEBULA_PASSWORD,
        CAASM_NEBULA_SPACE_NAME,
        [(CAASM_NEBULA_HOST, CAASM_NEBULA_PORT)],
    )
    app.nebula_sess_pool.init(SessionPoolConfig())
    yield
    logger.info("Closing asyncio redis ...")
    await app.redis.close()
    logger.info("Closing Nebula session pool ...")
    app.nebula_sess_pool.close()


app = App(lifespan=lifespan)


@app.exception_handler(Exception)
async def bussiness_exception_handler(req: Request, exception: Exception):
    if isinstance(exception, fernet.InvalidToken):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=RootModel[resp.Response](
                resp.Response(
                    code=status.HTTP_401_UNAUTHORIZED,
                    msg="{}: {}".format(exception.__class__.__name__, exception),
                )
            ).model_dump(),
        )
    elif isinstance(exception, AssertionError):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=RootModel[resp.Response](
                resp.Response(
                    code=status.HTTP_500_INTERNAL_SERVER_ERROR, msg=str(exception)
                )
            ).model_dump(),
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=RootModel[resp.Response](
            resp.Response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg="{}: {}".format(exception.__class__.__name__, exception),
            )
        ).model_dump(),
    )


app.include_router(router=api.v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
