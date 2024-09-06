#!/bin/env python3
import time
import json
import model
import msgpack
import hashlib

from common.app import App
from common.log import logger
from common.nebula import make_object
from typing import Optional, List, Dict
from deps.permission import PermissionChecker, LOGIN, LOGOUT
from fastapi import APIRouter, Request, Depends
from nebula3.common.ttypes import Row, Value, NMap, NList

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
    logger.info("user %s", user)
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
        data=make_object(model.User, props_dict, values[0].value.decode())
    )


@user_router.get(path="/user/menus", response_model=model.Response)
async def get_permission(req: Request, user: dict = Depends(LOGIN)):
    app: App = req.app
    logger.info("user %s", user)
    ngql = """LOOKUP ON caasm_perm_group WHERE caasm_perm_group.perm_group_name == 'menu' YIELD id(vertex) AS i \
        | GO FROM $-.i OVER perm_e_group REVERSELY YIELD src(edge) AS i \
        | GO 1 TO 4 STEPS FROM $-.i OVER perm_include, perm_e_role YIELD dst(edge) AS i, src(edge) AS j \
        | GO FROM $-.i OVER user_e_role REVERSELY WHERE $$.caasm_user.username == $username YIELD $-.j AS i \
        | GO 1 TO 4 STEPS FROM $-.i OVER perm_include YIELD properties($^) AS s, properties($$) AS t \
        | GROUP BY $-.s YIELD $-.s AS menu, collect($-.t) AS submenus"""
    result = app.nebula_sess_pool.execute_py(ngql, {"username": user.get("username")})
    menus_map: Dict[str, model.Perm] = {}
    data: dict[str, model.Perm] = {}
    for row in result.rows():
        assert isinstance(row, Row), "no_menus"
        menu_value = row.values[0]
        submenus_value = row.values[1]
        assert isinstance(menu_value, Value), "no_menus"
        assert isinstance(menu_value.value, NMap), "no_menus"
        menu = make_object(model.Perm, menu_value.value.kvs)
        menus_map[menu.perm_name] = menu
        assert isinstance(submenus_value, Value), "no_menus"
        logger.info("submenus_value %s", submenus_value.value)
        assert isinstance(submenus_value.value, NList), "no_menus"
        for sub_row in submenus_value.value.values:
            assert isinstance(sub_row, Value), "no_menus"
            assert isinstance(sub_row.value, NMap), "no_menus"
            submenu = make_object(model.Perm, sub_row.value.kvs)
            if submenu.perm_name in data.keys():
                menu.submenus.append(data.pop(submenu.perm_name))
            else:
                menus_map[submenu.perm_name] = submenu
                menu.submenus.append(submenu)
        tmp_menu = menus_map.get(menu.perm_name)
        if tmp_menu is not None:
            tmp_menu.submenus = menu.submenus
        menu.submenus.sort(key=lambda e: e.created_at)
        data[menu.perm_name] = menu
    logger.info("result %s", result)
    menus = list(data.values())
    menus.sort(key=lambda e: e.created_at)
    return model.Response(data=menus)


@user_router.get(path="/user/{user_id}", response_model=model.Response)
async def get_user(
    user_id: Optional[str],
    has_perms: bool = Depends(PermissionChecker(["get_anything"])),
):
    logger.info("user_id %s", user_id)
    return model.Response(data=has_perms)
