#!/bin/env python3
import time
import model
import msgpack
import hashlib

from common.app import App
from common.log import logger
from common.nebula import make_object
from typing import Optional, List, Dict, Annotated
from deps.permission import PermissionChecker, LOGIN, LOGOUT
from fastapi import APIRouter, Request, Depends, Header
from nebula3.common.ttypes import Row, Value, NMap
from settings import CAASM_TOKEN_KEY

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


@user_router.get(path="/user/action/logout", response_model=model.Response)
async def logout(logout: dict = Depends(LOGOUT)) -> model.Response:
    return model.Response(data=logout)


@user_router.get(path="/user", response_model=model.Response)
async def get_profile(req: Request, user: dict = Depends(LOGIN)):
    app: App = req.app
    logger.info("user_id %s", user)
    ngql = "LOOKUP ON caasm_user WHERE caasm_user.username == $username YIELD id(VERTEX) AS id, properties(VERTEX) AS props"
    result = app.nebula_sess_pool.execute_py(ngql, {"username": user.get("username")})
    rows: Optional[List[Row]] = result.rows()
    assert rows, "no_this_user"
    row = rows[0]
    values: Optional[List[Value]] = row.values
    assert values, "no_this_user"
    props: Optional[NMap] = values[1].value
    assert props, "no_this_user"
    props_dict: Dict[bytes, Value] = props.kvs
    assert isinstance(values[0].value, bytes), "model_mismatch"
    return model.Response(
        data=make_object(model.User, values[0].value.decode(), props_dict)
    )


@user_router.get(path="/user/{user_id}", response_model=model.Response)
async def get_user(
    user_id: Optional[str],
    has_perms: bool = Depends(PermissionChecker(["get_anything"])),
):
    logger.info("user_id %s", user_id)
    return model.Response(data=has_perms)
