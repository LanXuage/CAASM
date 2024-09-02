#!/bin/env python3
import io
import base64
import string
import random

from model import Response
from datetime import timedelta
from fastapi import Request
from common.app import App
from common.log import logger
from fastapi import APIRouter

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
