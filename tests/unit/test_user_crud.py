#!/bin/env python3
"""
Unit tests for user management CRUD API endpoints.
"""

import hashlib
import time
import msgpack
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet

from nebula3.common.ttypes import Value, Vertex, Tag, Row
from common.app import App
from common.websocket import WebSocketManager
from common.file import FileManager
from captcha.image import ImageCaptcha
from fastapi import status, Request
from fastapi.responses import JSONResponse
from model import resp
from pydantic import RootModel
from cryptography import fernet as fernet_mod


# ========== Helpers ==========

def _make_value(val):
    v = Value()
    v.value = val
    return v


def _make_value_with_vertex(vertex):
    v = Value()
    v.value = vertex
    v.get_vVal = MagicMock(return_value=vertex)
    return v


def _make_perm_pass_result():
    result = MagicMock()
    result.is_succeeded.return_value = True
    result.row_size.return_value = 0
    result.rows.return_value = []
    return result


def _make_query_result(rows=None, row_size=None):
    result = MagicMock()
    result.is_succeeded.return_value = True
    if rows is not None:
        result.rows.return_value = rows
    if row_size is not None:
        result.row_size.return_value = row_size
    return result


def _make_user_vertex(vid_str: str, username: str, real_name: str = "Test User"):
    vertex = Vertex()
    vid = MagicMock()
    vid.get_sVal.return_value = vid_str.encode()
    vertex.vid = vid
    tag = Tag()
    tag.props = {
        b"username": _make_value(username.encode()),
        b"real_name": _make_value(real_name.encode()),
        b"phone": _make_value(b"123456"),
        b"email": _make_value(b"test@test.com"),
        b"user_status": _make_value(1),
        b"updated_at": _make_value(int(time.time())),
        b"created_at": _make_value(int(time.time())),
    }
    vertex.tags = [tag]
    return vertex


# ========== Fixtures ==========

@pytest.fixture
def mock_nebula():
    mock = MagicMock()
    mock.execute.return_value = _make_query_result([], 0)
    mock.fetch.return_value = None
    return mock


@pytest.fixture
def mock_redis():
    return AsyncMock()


@pytest.fixture
def app_with_mocks(mock_nebula, mock_redis):
    app = App()
    app.token_fernet = Fernet(Fernet.generate_key())
    app.invalid_tokens = set()
    app.token_ttl = 30000
    app.image_captcha = ImageCaptcha(width=320, height=120, font_sizes=(62, 70, 76))
    app.redis = mock_redis
    app.nebula_facade = mock_nebula
    app.notify_queue = MagicMock()
    app.task_queue = AsyncMock()
    app.file_manager = FileManager()
    app.websocket_manager = WebSocketManager(app.notify_queue)

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exception: Exception):
        if isinstance(exception, fernet_mod.InvalidToken):
            return JSONResponse(status_code=status.HTTP_200_OK,
                content=RootModel[resp.Response](resp.Response(code=status.HTTP_401_UNAUTHORIZED, data="invalid_token")).model_dump())
        elif isinstance(exception, AssertionError):
            return JSONResponse(status_code=status.HTTP_200_OK,
                content=RootModel[resp.Response](resp.Response(code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=str(exception))).model_dump())
        return JSONResponse(status_code=status.HTTP_200_OK,
            content=RootModel[resp.Response](resp.Response(code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=f"{exception.__class__.__name__}: {exception}")).model_dump())

    from api import router
    app.include_router(router=router)
    return app


@pytest.fixture
def client(app_with_mocks):
    return TestClient(app_with_mocks, raise_server_exceptions=False)


@pytest.fixture
def auth_headers(app_with_mocks):
    ctime = int(time.time())
    data = msgpack.packb({"username": "admin"})
    token = app_with_mocks.token_fernet.encrypt_at_time(data, ctime).decode()
    return {"X-Token": token}


# ========== Tests ==========

class TestUserCRUD:

    def test_list_users_empty(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_list_users(self, client, auth_headers, mock_nebula):
        vertex = _make_user_vertex("test_vid", "testuser")
        row = Row()
        val = Value()
        val.value = vertex
        val.get_vVal = MagicMock(return_value=vertex)
        row.values = [val]
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([row], 1)]
        response = client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["username"] == "testuser"

    def test_create_user(self, client, auth_headers, mock_nebula):
        from shared.nebula import gen_vid
        test_vid = gen_vid("caasm_user", "newuser")
        vertex = _make_user_vertex(test_vid, "newuser", "New User")
        mock_nebula.fetch.side_effect = [None, vertex]
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.post("/api/v1/user", json={
            "username": "newuser", "password": "password123",
            "realName": "New User", "phone": "987654321",
            "email": "new@test.com", "userStatus": 1,
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["username"] == "newuser"

    def test_create_duplicate_user(self, client, auth_headers, mock_nebula):
        mock_nebula.fetch.return_value = _make_user_vertex("vid", "existing")
        mock_nebula.execute.side_effect = [_make_perm_pass_result()]
        response = client.post("/api/v1/user", json={"username": "existing", "password": "x"}, headers=auth_headers)
        assert response.json()["code"] == 500

    def test_update_user(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.put("/api/v1/user/test_vid", json={"realName": "Updated", "phone": "111"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_delete_user(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.delete("/api/v1/user/test_vid", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_change_user_status(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.post("/api/v1/user/test_vid/status", json={"userStatus": 2}, headers=auth_headers)
        assert response.status_code == 200

    def test_assign_roles(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([]), _make_query_result([], 0)]
        response = client.post("/api/v1/user/test_vid/roles", json={"roleIds": ["r1", "r2"]}, headers=auth_headers)
        assert response.status_code == 200

    def test_get_user_detail(self, client, auth_headers, mock_nebula):
        vertex = _make_user_vertex("test_vid", "testuser")
        mock_nebula.fetch.return_value = vertex
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([])]
        response = client.get("/api/v1/user/test_vid", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["username"] == "testuser"