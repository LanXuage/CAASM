#!/bin/env python3
import io
import base64
import string
import random

from model import Response
from datetime import timedelta
from fastapi.websockets import WebSocketState
from fastapi import Request, WebSocket, Depends
from deps.permission import LOGIN, PermissionChecker
from common.app import App
from common.log import logger
from fastapi import APIRouter, UploadFile

common_router = APIRouter()


@common_router.get(path="/captcha", response_model=Response)
async def get_captcha(s: str, req: Request):
    app: App = req.app
    captcha = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(5)]
    )
    logger.info("s %s, captcha %s", s, captcha)
    await app.redis.set(f"captcha_{s}", captcha.lower(), timedelta(minutes=5))
    logger.info("s %s", await app.redis.get(f"captcha_{s}"))
    data: io.BytesIO = app.image_captcha.generate(captcha)
    return Response(data=base64.b64encode(data.read()).decode())


@common_router.websocket(path="/notify")
async def notify(req: Request, websocket: WebSocket, user: dict = Depends(LOGIN)):
    app: App = req.app
    username = user.get("username")
    await app.websocket_manager.add_websocket(username, websocket)
    while True:
        try:
            event = await websocket.receive_json()
            await app.websocket_manager.process_event(event, username)
        except BaseException as e:
            logger.warning("websocket of %s warning", username, exc_info=e)
        if websocket.state == WebSocketState.DISCONNECTED:
            break


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
