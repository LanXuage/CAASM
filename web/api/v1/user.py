#!/bin/env python3
import time
import model
import msgpack
import hashlib

from common.app import App
from datetime import datetime
from common.log import logger
from common.datetime import ZONE_INFO
from common.nebula import make_object, gen_vid
from typing import Optional, List, Dict
from deps.permission import PermissionChecker, LOGIN, LOGOUT
from fastapi import APIRouter, Request, Depends
from nebula3.common.ttypes import Row, Value, NList, Vertex

user_router = APIRouter()
USER_TAG = "caasm_user"

# ==================== Auth endpoints ====================


@user_router.post(path="/user/action/login", response_model=model.Response)
async def login(login_req: model.LoginRequest, req: Request) -> model.Response:
    app: App = req.app
    captcha = await app.redis.getdel(f"captcha_{login_req.s}")
    logger.info("login %s, captcha %s", login_req, captcha)
    assert captcha == login_req.captcha.lower().encode(), "invalid_captcha"
    logger.info("valid capthca")
    stmt = "LOOKUP ON caasm_user WHERE caasm_user.username == $username YIELD properties(VERTEX).passwd AS passwd"
    result = app.nebula_facade.execute(stmt, username=login_req.username)
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
    ctime = int(time.time())
    token = app.token_fernet.encrypt_at_time(data=msgpack.packb({"username": login_req.username}), current_time=ctime).decode()  # type: ignore
    return model.Response(
        data=model.Token(
            token, datetime.fromtimestamp(ctime + app.token_ttl, tz=ZONE_INFO)
        )
    )


@user_router.get(path="/user/action/logout", response_model=model.Response)
async def logout(logout: dict = Depends(LOGOUT)) -> model.Response:
    return model.Response(data=logout)


@user_router.get(path="/user", response_model=model.Response)
async def get_profile(req: Request, user: dict = Depends(LOGIN)):
    app: App = req.app
    logger.info("user %s", user)
    stmt = (
        "LOOKUP ON caasm_user WHERE caasm_user.username == $username YIELD VERTEX AS v"
    )
    result = app.nebula_facade.execute(stmt, username=user.get("username"))
    logger.info("result %s", result)
    rows: Optional[List[Row]] = result.rows()
    assert rows, "no_this_user"
    row = rows[0]
    logger.info("row %s", row)
    values: Optional[List[Value]] = row.values
    assert values, "no_this_user"
    vertex: Optional[Vertex] = values[0].value
    assert isinstance(vertex, Vertex), "no_this_user"
    return model.Response(data=make_object(model.User, vertex))


@user_router.get(path="/user/menus", response_model=model.Response)
async def get_permission(req: Request, user: dict = Depends(LOGIN)):
    app: App = req.app
    logger.info("user %s", user)
    stmt = """LOOKUP ON caasm_perm_group WHERE caasm_perm_group.perm_group_name == 'menu' YIELD id(vertex) AS i \
        | GO FROM $-.i OVER perm_e_group REVERSELY YIELD src(edge) AS i \
        | GO 1 TO 4 STEPS FROM $-.i OVER perm_include, perm_e_role YIELD dst(edge) AS i, src(edge) AS j \
        | GO FROM $-.i OVER user_e_role REVERSELY WHERE $$.caasm_user.username == $username YIELD $-.j AS i \
        | GO 1 TO 4 STEPS FROM $-.i OVER perm_include YIELD $^ AS s, $$ AS t \
        | GROUP BY $-.s YIELD $-.s AS menu, collect($-.t) AS submenus"""
    result = app.nebula_facade.execute(stmt, username=user.get("username"))
    menus_map: Dict[str, model.Perm] = {}
    data: dict[str, model.Perm] = {}
    for row in result.rows():
        assert isinstance(row, Row), "no_menus"
        menu_value = row.values[0]
        submenus_value = row.values[1]
        assert isinstance(menu_value, Value), "no_menus"
        assert isinstance(menu_value.value, Vertex), "no_menus"
        menu = make_object(model.Perm, menu_value.value)
        menus_map[menu.perm_name] = menu
        assert isinstance(submenus_value, Value), "no_menus"
        logger.info("submenus_value %s", submenus_value.value)
        assert isinstance(submenus_value.value, NList), "no_menus"
        for sub_row in submenus_value.value.values:
            assert isinstance(sub_row, Value), "no_menus"
            assert isinstance(sub_row.value, Vertex), "no_menus"
            submenu = make_object(model.Perm, sub_row.value)
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


# ==================== User management CRUD endpoints ====================


@user_router.get(path="/users", response_model=model.Response)
async def list_users(
    req: Request,
    _: bool = Depends(PermissionChecker(["user_read_permission"])),
) -> model.Response:
    """List all users."""
    app: App = req.app
    stmt = "LOOKUP ON {} YIELD VERTEX AS v".format(USER_TAG)
    result = app.nebula_facade.execute(stmt)
    users: List[model.User] = []
    for row in result.rows():
        assert isinstance(row, Row) and isinstance(row.values[0], Value), "server_err"
        vertex = row.values[0].get_vVal()
        if isinstance(vertex, Vertex):
            users.append(make_object(model.User, vertex))
    return model.Response(data=users)


@user_router.post(path="/user", response_model=model.Response)
async def create_user(
    req: Request,
    user_create: model.UserCreate,
    _: bool = Depends(PermissionChecker(["user_create_permission"])),
) -> model.Response:
    """Create a new user."""
    app: App = req.app
    vid = gen_vid(USER_TAG, user_create.username)

    # Check if user already exists
    existing = app.nebula_facade.fetch(USER_TAG, vid)
    assert existing is None, "user_exist"

    # Hash the password with SHA256 (consistent with the login flow)
    passwd_hash = hashlib.sha256(user_create.password.encode()).hexdigest()

    stmt = (
        'INSERT VERTEX IF NOT EXISTS {}(username, passwd, real_name, phone, email, user_status) '
        'VALUES "{}":($username, $passwd, $real_name, $phone, $email, $user_status)'
    ).format(USER_TAG, vid)
    result = app.nebula_facade.execute(
        stmt,
        username=user_create.username,
        passwd=passwd_hash,
        real_name=user_create.real_name,
        phone=user_create.phone,
        email=user_create.email,
        user_status=user_create.user_status,
    )
    assert result.is_succeeded(), "server_err"

    # Fetch the created user
    vertex = app.nebula_facade.fetch(USER_TAG, vid)
    assert isinstance(vertex, Vertex), "server_err"
    return model.Response(data=make_object(model.User, vertex))


@user_router.get(path="/user/{user_id}", response_model=model.Response)
async def get_user(
    req: Request,
    user_id: str,
    _: bool = Depends(PermissionChecker(["user_read_permission"])),
) -> model.Response:
    """Get user details with roles."""
    app: App = req.app
    logger.info("get user %s", user_id)

    vertex = app.nebula_facade.fetch(USER_TAG, user_id)
    assert isinstance(vertex, Vertex), "user_not_found"

    # Get user's roles
    roles: List[str] = []
    stmt = (
        'GO FROM "{}" OVER user_e_role '
        "YIELD $$.caasm_role.role_name AS role_name"
    ).format(user_id)
    result = app.nebula_facade.execute(stmt)
    if result.is_succeeded():
        for row in result.rows():
            if row.values and row.values[0]:
                role_name = row.values[0].get_sVal()
                if role_name:
                    roles.append(role_name.decode() if isinstance(role_name, bytes) else role_name)

    user_obj = make_object(model.UserDetail, vertex, roles=roles)
    return model.Response(data=user_obj)


@user_router.put(path="/user/{user_id}", response_model=model.Response)
async def update_user(
    req: Request,
    user_id: str,
    user_update: model.UserUpdate,
    _: bool = Depends(PermissionChecker(["user_modify_permission"])),
) -> model.Response:
    """Update user information."""
    app: App = req.app

    # Build SET clause dynamically for non-None fields
    set_parts = []
    params = {}
    if user_update.real_name is not None:
        set_parts.append("real_name=$real_name")
        params["real_name"] = user_update.real_name
    if user_update.phone is not None:
        set_parts.append("phone=$phone")
        params["phone"] = user_update.phone
    if user_update.email is not None:
        set_parts.append("email=$email")
        params["email"] = user_update.email
    if user_update.user_status is not None:
        set_parts.append("user_status=$user_status")
        params["user_status"] = user_update.user_status

    if not set_parts:
        return model.Response(data="no_fields_to_update")

    set_parts.append("updated_at=now()")
    stmt = 'UPDATE VERTEX ON {} "{}" SET {}'.format(
        USER_TAG, user_id, ", ".join(set_parts)
    )
    result = app.nebula_facade.execute(stmt, **params)
    assert result.is_succeeded(), "server_err"

    return model.Response(data="updated")


@user_router.delete(path="/user/{user_id}", response_model=model.Response)
async def delete_user(
    req: Request,
    user_id: str,
    _: bool = Depends(PermissionChecker(["user_modify_permission"])),
) -> model.Response:
    """Delete a user and all associated edges."""
    app: App = req.app
    stmt = 'DELETE VERTEX "{}" WITH EDGE'.format(user_id)
    result = app.nebula_facade.execute(stmt)
    assert result.is_succeeded(), "server_err"
    return model.Response(data="deleted")


@user_router.post(path="/user/{user_id}/status", response_model=model.Response)
async def change_user_status(
    req: Request,
    user_id: str,
    status_change: model.UserStatusChange,
    _: bool = Depends(PermissionChecker(["user_modify_permission"])),
) -> model.Response:
    """Enable or disable a user account."""
    app: App = req.app
    stmt = 'UPDATE VERTEX ON {} "{}" SET user_status=$user_status, updated_at=now()'.format(
        USER_TAG, user_id
    )
    result = app.nebula_facade.execute(stmt, user_status=status_change.user_status)
    assert result.is_succeeded(), "server_err"
    return model.Response(data="status_updated")


@user_router.post(path="/user/{user_id}/roles", response_model=model.Response)
async def assign_user_roles(
    req: Request,
    user_id: str,
    role_assign: model.UserAssignRoles,
    _: bool = Depends(PermissionChecker(["user_modify_permission"])),
) -> model.Response:
    """Assign roles to a user. Replaces existing role assignments."""
    app: App = req.app

    # Delete existing role assignments
    del_stmt = 'GO FROM "{}" OVER user_e_role YIELD src(edge) AS src, dst(edge) AS dst, rank(edge) AS rank | DELETE EDGE user_e_role $-.src -> $-.dst @ $-.rank'.format(
        user_id
    )
    app.nebula_facade.execute(del_stmt)

    # Insert new role assignments
    if role_assign.role_ids:
        insert_stmt = "INSERT EDGE IF NOT EXISTS user_e_role() VALUES "
        for role_id in role_assign.role_ids:
            insert_stmt += '"{}"->"{}":(),'.format(user_id, role_id)
        result = app.nebula_facade.execute(insert_stmt[:-1])
        assert result.is_succeeded(), "server_err"

    return model.Response(data="roles_assigned")