#!/bin/env python
import time
import msgpack

from enum import Enum
from common.app import App
from common.log import logger
from fastapi import Header, Request, Depends
from typing import Any, Annotated, List, Union, Optional
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
        self, token: Annotated[str, Header(alias=CAASM_TOKEN_KEY)], req: Request
    ) -> Union[bool, dict]:
        app: App = req.app
        if self.logout and token:
            app.invalid_tokens.add(token)
            return True
        if self.required == LoginState.NOCARE:
            return True
        try:
            logger.info("token %s, invalid_tokens %s", token, app.invalid_tokens)
            assert (
                self.required != LoginState.LOGIN or token not in app.invalid_tokens
            ), "invalid_token"
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

    async def __call__(self, req: Request, user_id: str = Depends(LOGIN)) -> bool:
        logger.info("has perm %s", self.permissions)
        return False
