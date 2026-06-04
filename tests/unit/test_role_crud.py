#!/bin/env python3
"""
Unit tests for role management CRUD API.
"""

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


def _make_perm_pass_result():
    result = MagicMock()
    result.is_succeeded.return_value = True
    result.row_size.return_value = 0
    result.rows.return_value = []
    return result


def _make_query_result(rows=None, row_size=None, succeeded=True):
    result = MagicMock()
    result.is_succeeded.return_value = succeeded
    if rows is not None:
        result.rows.return_value = rows
    if row_size is not None:
        result.row_size.return_value = row_size
    return result


def _make_role_vertex(vid_str: str, role_name: str, role_desc: str = "test desc"):
    vertex = Vertex()
    vid = MagicMock()
    vid.get_sVal.return_value = vid_str.encode()
    vertex.vid = vid
    tag = Tag()
    tag.props = {
        b"role_name": _make_value(role_name.encode()),
        b"role_desc": _make_value(role_desc.encode()),
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

class TestRoleCRUD:

    def test_list_roles_empty(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.get("/api/v1/roles", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_list_roles(self, client, auth_headers, mock_nebula):
        vertex = _make_role_vertex("role_vid", "Admin")
        row = Row()
        val = Value()
        val.value = vertex
        val.get_vVal = MagicMock(return_value=vertex)
        row.values = [val]
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([row], 1)]
        response = client.get("/api/v1/roles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["roleName"] == "Admin"

    def test_create_role(self, client, auth_headers, mock_nebula):
        from shared.nebula import gen_vid
        vid = gen_vid("caasm_role", "NewRole")
        vertex = _make_role_vertex(vid, "NewRole")
        mock_nebula.fetch.side_effect = [None, vertex]
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.post("/api/v1/role", json={"roleName": "NewRole", "roleDesc": "desc"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["roleName"] == "NewRole"

    def test_create_duplicate_role(self, client, auth_headers, mock_nebula):
        mock_nebula.fetch.return_value = _make_role_vertex("vid", "Existing")
        mock_nebula.execute.side_effect = [_make_perm_pass_result()]
        response = client.post("/api/v1/role", json={"roleName": "Existing"}, headers=auth_headers)
        assert response.json()["code"] == 500

    def test_get_role(self, client, auth_headers, mock_nebula):
        vertex = _make_role_vertex("role_vid", "Admin")
        mock_nebula.fetch.return_value = vertex
        # perm check + 2 relation queries
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([]), _make_query_result([])]
        response = client.get("/api/v1/role/role_vid", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["roleName"] == "Admin"

    def test_update_role(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.put("/api/v1/role/role_vid", json={"roleDesc": "new desc"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_delete_role(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.delete("/api/v1/role/role_vid", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_assign_perms(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([]), _make_query_result([], 0)]
        response = client.post("/api/v1/role/role_vid/perms", json={"permIds": ["p1", "p2"]}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_assign_users(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([]), _make_query_result([], 0)]
        response = client.post("/api/v1/role/role_vid/users", json={"userIds": ["u1"]}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_set_inherit(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([]), _make_query_result([], 0)]
        response = client.post("/api/v1/role/role_vid/inherit", json={"parentRoleId": "parent_vid"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200

    def test_set_mutex(self, client, auth_headers, mock_nebula):
        mock_nebula.execute.side_effect = [_make_perm_pass_result(), _make_query_result([], 0)]
        response = client.post("/api/v1/role/role_vid/mutex", json={"mutexRoleId": "mutex_vid"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 200