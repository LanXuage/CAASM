#!/bin/env python3
import io
import time
import base64
import string
import random
import msgpack

from model import Response
from datetime import timedelta
from fastapi import (
    Request,
    Response as FastResponse,
    WebSocket,
    Depends,
    APIRouter,
    UploadFile,
)
from deps.permission import PermissionChecker
from common.app import App
from common.log import logger
from settings import CAASM_TOKEN_TTL

common_router = APIRouter()


@common_router.get(path="/captcha")
async def get_captcha(s: str, req: Request):
    app: App = req.app
    captcha = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(5)]
    )
    logger.info("s %s, captcha %s", s, captcha)
    await app.redis.set(f"captcha_{s}", captcha.lower(), timedelta(minutes=5))
    logger.info("s %s", await app.redis.get(f"captcha_{s}"))
    data: io.BytesIO = app.image_captcha.generate(captcha)
    return FastResponse(content=data.read(), media_type="image/png")


@common_router.websocket(path="/notify")
async def notify(websocket: WebSocket, t: str):
    app: App = websocket.app
    data: dict = msgpack.unpackb(
        app.token_fernet.decrypt_at_time(
            token=t, ttl=CAASM_TOKEN_TTL, current_time=int(time.time())
        )
    )
    username = data.get("username")
    await app.websocket_manager.add_websocket(username, websocket)
    # while True:
    #     try:
    #         event = await websocket.receive_json()
    #         await app.websocket_manager.process_event(event, username)
    #     except BaseException as e:
    #         logger.warning("websocket of %s warning", username, exc_info=e)
    #         await asyncio.sleep(1)
    #     if websocket.state == WebSocketState.DISCONNECTED:
    #         break


@common_router.post(path="/upload", response_model=Response)
async def upload(
    req: Request,
    file: UploadFile,
    _: bool = Depends(PermissionChecker(["file_upload_permission"])),
):
    app: App = req.app
    assert file.filename is not None, "must_has_filename"
    await app.file_manager.save(file.filename, file)
    logger.info("file %s", file)
    logger.info("filename %s", file.filename)
    logger.info("size %s", file.size)
    logger.info("content_type %s", file.content_type)
    await file.close()
    return Response(data=file.filename)
