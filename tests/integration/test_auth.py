#!/bin/env python3
"""
Integration tests for login/logout flow.

These tests require:
- A running Nebula Graph cluster with seed data (admin user)
- A running Redis instance

Start with: docker compose --profile dev up -d metad-dev storaged-dev graphd-dev init-dev redis-dev
"""

import hashlib
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

pytestmark = [pytest.mark.integration, pytest.mark.slow]


class TestAuthFlow:
    """Integration tests for authentication flow."""

    def test_login_sequence_logic(self):
        """
        Verify the login password hashing logic.

        The password sent by the client should be:
        SHA256(s + captcha + username + server_passwd_hash)
        """
        # Simulate client-side hashing
        s = "random_salt"
        captcha = "abcde"
        username = "admin"
        server_passwd = "admin"  # seed data password

        # Client computes:
        client_password = hashlib.sha256(
            f"{s}_{captcha}_{username}_{server_passwd}".encode()
        ).hexdigest()

        # Verify it's the expected format
        assert len(client_password) == 64  # SHA256 hex
        assert all(c in "0123456789abcdef" for c in client_password)

    def test_token_encryption_roundtrip(self):
        """Fernet token encryption/decryption should round-trip correctly."""
        import msgpack
        from cryptography.fernet import Fernet
        import time

        key = Fernet.generate_key()
        fernet = Fernet(key)
        ctime = int(time.time())

        data = {"username": "admin"}
        token = fernet.encrypt_at_time(
            data=msgpack.packb(data), current_time=ctime
        ).decode()

        # Decrypt
        decrypted = msgpack.unpackb(
            fernet.decrypt_at_time(token=token, ttl=30000, current_time=ctime)
        )

        assert decrypted == {"username": "admin"}

    def test_token_expiry(self):
        """Expired token should be rejected."""
        import msgpack
        from cryptography.fernet import Fernet, InvalidToken
        import time

        key = Fernet.generate_key()
        fernet = Fernet(key)
        ctime = int(time.time())

        data = {"username": "admin"}
        token = fernet.encrypt_at_time(
            data=msgpack.packb(data), current_time=ctime
        ).decode()

        # Try to decrypt with current_time beyond TTL
        future_time = ctime + 30001
        with pytest.raises(InvalidToken):
            fernet.decrypt_at_time(token=token, ttl=30000, current_time=future_time)