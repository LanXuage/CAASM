#!/bin/env python
import time
import msgpack

from enum import Enum
from common.app import App
from common.log import logger
from fastapi import Header, Request, Depends, WebSocket
from typing import Annotated, List, Union, Optional
from settings import CAASM_TOKEN_KEY, CAASM_TOKEN_TTL


class LoginState(Enum):
    NOLOGIN = 0
    LOGIN = 1
    NOCARE = 2


class LoginChecker:
    def __init__(self, required: LoginState, logout: bool = False) -> None:
        self.required = required
        self.logout = logout

    async def __call__(
        self,
        req: Request,
        token: Annotated[Optional[str], Header(alias=CAASM_TOKEN_KEY)] = None,
    ) -> Union[bool, dict]:
        app: App = req.app
        if self.logout and token:
            app.invalid_tokens.add(token)
            return True
        if self.required == LoginState.NOCARE:
            return True
        try:
            assert (
                self.required != LoginState.LOGIN or token not in app.invalid_tokens
            ) and token, "invalid_token"
            data = msgpack.unpackb(
                app.token_fernet.decrypt_at_time(
                    token=token, ttl=CAASM_TOKEN_TTL, current_time=int(time.time())
                )
            )
        except BaseException as e:
            if self.required == LoginState.LOGIN:
                raise e
        return data


LOGOUT = LoginChecker(LoginState.LOGIN, logout=True)
LOGIN = LoginChecker(LoginState.LOGIN)
NOLOGIN = LoginChecker(LoginState.LOGIN)
NOCARE = LoginChecker(LoginState.NOCARE)


class PermissionChecker:
    def __init__(self, permissions: List[str], throw_except: bool = True) -> None:
        self.permissions = permissions
        self.throw_except = throw_except

    async def __call__(
        self, req: Request, user: dict = Depends(LOGIN)
    ) -> Union[bool, dict]:
        app: App = req.app
        stmt = """UNWIND $perms AS perm_name MINUS (LOOKUP ON caasm_user WHERE caasm_user.username == $username YIELD id(VERTEX) AS id \
            | GO FROM $-.id OVER user_e_role YIELD dst(EDGE) AS id \
            | GO FROM $-.id OVER perm_e_role REVERSELY YIELD $$.caasm_perm.perm_name AS perm_name)"""
        logger.info("has perm %s", self.permissions)
        result = app.nebula_facade.execute(
            stmt, username=user.get("username"), perms=self.permissions
        )
        f = result.is_succeeded() and result.row_size() == 0
        if self.throw_except:
            assert f, "no_perm"
        logger.info("result %s", result.row_size())
        return user if f else f
