#!/bin/env python3
"""
Unit tests for permission system (LoginChecker, PermissionChecker).

Uses mock NebulaFacade and mock Fernet token to test auth logic.
"""

import time
import msgpack
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from cryptography.fernet import Fernet

# We need to mock the App and settings before importing the permission module
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web"))


@pytest.fixture
def fernet_key():
    """Generate a valid Fernet key for testing."""
    return Fernet.generate_key()


@pytest.fixture
def mock_app(fernet_key):
    """Create a mock App with required attributes."""
    app = MagicMock()
    app.token_fernet = Fernet(fernet_key)
    app.invalid_tokens = set()
    app.token_ttl = 30000
    app.nebula_facade = MagicMock()
    return app


@pytest.fixture
def valid_token(mock_app):
    """Create a valid Fernet token."""
    ctime = int(time.time())
    data = msgpack.packb({"username": "admin"})
    return mock_app.token_fernet.encrypt_at_time(data, ctime).decode()


class TestLoginChecker:
    """Tests for LoginChecker dependency."""

    def test_login_checker_valid_token(self, mock_app, valid_token):
        """Valid token should return user data."""
        from deps.permission import LoginChecker, LoginState
        import asyncio

        checker = LoginChecker(LoginState.LOGIN)

        req = MagicMock()
        req.app = mock_app

        result = asyncio.run(checker(req, token=valid_token))
        assert result == {"username": "admin"}

    def test_login_checker_no_token(self, mock_app):
        """Missing token should raise an error."""
        from deps.permission import LoginChecker, LoginState
        import asyncio

        checker = LoginChecker(LoginState.LOGIN)

        req = MagicMock()
        req.app = mock_app

        with pytest.raises(Exception):
            asyncio.run(checker(req, token=None))

    def test_login_checker_invalidated_token(self, mock_app, valid_token):
        """Token in invalid_tokens set should be rejected."""
        from deps.permission import LoginChecker, LoginState
        import asyncio

        mock_app.invalid_tokens.add(valid_token)

        checker = LoginChecker(LoginState.LOGIN)

        req = MagicMock()
        req.app = mock_app

        with pytest.raises(AssertionError):
            asyncio.run(checker(req, token=valid_token))

    def test_login_checker_logout(self, mock_app, valid_token):
        """LOGOUT should add token to invalid_tokens and return True."""
        from deps.permission import LoginChecker, LoginState
        import asyncio

        checker = LoginChecker(LoginState.LOGIN, logout=True)

        req = MagicMock()
        req.app = mock_app

        result = asyncio.run(checker(req, token=valid_token))
        assert result is True
        assert valid_token in mock_app.invalid_tokens

    def test_login_checker_nocare(self, mock_app):
        """NOCARE state should always return True."""
        from deps.permission import LoginChecker, LoginState
        import asyncio

        checker = LoginChecker(LoginState.NOCARE)

        req = MagicMock()
        req.app = mock_app

        result = asyncio.run(checker(req, token=None))
        assert result is True

    def test_login_checker_invalid_token_format(self, mock_app):
        """Malformed token should raise error."""
        from deps.permission import LoginChecker, LoginState
        import asyncio

        checker = LoginChecker(LoginState.LOGIN)

        req = MagicMock()
        req.app = mock_app

        with pytest.raises(Exception):
            asyncio.run(checker(req, token="invalid_token_string"))


class TestPermissionChecker:
    """Tests for PermissionChecker dependency."""

    @pytest.fixture
    def mock_result_has_perm(self):
        """Mock ResultSet indicating user has all requested permissions."""
        result = MagicMock()
        result.is_succeeded.return_value = True
        result.row_size.return_value = 0  # MINUS returns empty = all perms granted
        return result

    @pytest.fixture
    def mock_result_no_perm(self):
        """Mock ResultSet indicating user lacks some permissions."""
        result = MagicMock()
        result.is_succeeded.return_value = True
        result.row_size.return_value = 2  # MINUS returned 2 = missing perms
        return result

    def test_permission_checker_has_perm(self, mock_app, mock_result_has_perm):
        """User has all requested permissions."""
        from deps.permission import PermissionChecker
        import asyncio

        mock_app.nebula_facade.execute.return_value = mock_result_has_perm

        checker = PermissionChecker(["field_create_permission"])

        req = MagicMock()
        req.app = mock_app

        # Pass user dict directly (bypass LoginChecker)
        result = asyncio.run(checker(req, user={"username": "admin"}))
        assert result == {"username": "admin"}

    def test_permission_checker_no_perm(self, mock_app, mock_result_no_perm):
        """User lacks requested permissions - should raise AssertionError."""
        from deps.permission import PermissionChecker
        import asyncio

        mock_app.nebula_facade.execute.return_value = mock_result_no_perm

        checker = PermissionChecker(["field_create_permission"])

        req = MagicMock()
        req.app = mock_app

        with pytest.raises(AssertionError):
            asyncio.run(checker(req, user={"username": "guest"}))

    def test_permission_checker_no_throw(self, mock_app, mock_result_no_perm):
        """With throw_except=False, should return False instead of raising."""
        from deps.permission import PermissionChecker
        import asyncio

        mock_app.nebula_facade.execute.return_value = mock_result_no_perm

        checker = PermissionChecker(["field_create_permission"], throw_except=False)

        req = MagicMock()
        req.app = mock_app

        result = asyncio.run(checker(req, user={"username": "guest"}))
        assert result is False

    def test_permission_checker_correct_nsql_params(self, mock_app, mock_result_has_perm):
        """Verify correct nGQL parameters are passed to NebulaFacade."""
        from deps.permission import PermissionChecker
        import asyncio

        mock_app.nebula_facade.execute.return_value = mock_result_has_perm

        checker = PermissionChecker(["perm_a", "perm_b"])

        req = MagicMock()
        req.app = mock_app

        asyncio.run(checker(req, user={"username": "testuser"}))

        # Verify execute was called with correct params
        call_args = mock_app.nebula_facade.execute.call_args
        assert call_args is not None
        # username should be "testuser"
        assert call_args.kwargs.get("username") == "testuser"
        # perms should be the list we passed
        assert call_args.kwargs.get("perms") == ["perm_a", "perm_b"]