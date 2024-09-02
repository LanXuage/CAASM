#!/bin/env python3
import time
import model
import msgpack
import hashlib

from common.app import App
from common.log import logger
from fastapi import APIRouter, Request

user_router = APIRouter()


@user_router.post(path="/user/action/login", response_model=model.Response)
async def login(login_req: model.LoginRequest, req: Request) -> model.Response:
    app: App = req.app
    captcha = await app.redis.getdel(f"captcha_{login_req.s}")
    logger.info("login %s, captcha %s", login_req, captcha)
    assert captcha == login_req.captcha.lower().encode(), "invalid_captcha"
    logger.info("valid capthca")
    ngql = "LOOKUP ON caasm_user WHERE caasm_user.username == $username YIELD properties(VERTEX).passwd AS passwd"
    result = app.nebula_sess_pool.execute_py(ngql, {"username": login_req.username})
    assert result.is_succeeded(), result.error_msg()
    passwds = result.column_values("passwd")
    assert len(passwds) > 0, "invalid_username_or_password"
    password = hashlib.sha256(
        f"{login_req.s}_{login_req.captcha}_{login_req.username}_{passwds[0].as_string()}".encode()
    ).hexdigest()
    logger.info(
        "res %s, pass %s, password %s", result, passwds[0].as_string(), password
    )
    assert password == login_req.password, "invalid_username_or_password"
    logger.info("valid passwd")
    token = app.token_fernet.encrypt_at_time(data=msgpack.packb({"username": login_req.username}), current_time=int(time.time())).decode()  # type: ignore
    return model.Response(data=token)
