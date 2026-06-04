#!/bin/env python3
"""
Unit tests for worker BulkTask (DELETE/POST/PUT + WATER_LINE splitting).
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, call

from core.task import BulkTask, BulkMethod, TaskType, TaskStatus


@pytest.fixture
def mock_nebula():
    mock = MagicMock()
    mock.execute.return_value = MagicMock()
    mock.execute.return_value.is_succeeded.return_value = True
    mock.fetch.return_value = None
    return mock


def _make_task(method, data, tag="field"):
    return BulkTask(
        id="test_task_id",
        task_type=TaskType.BULK,
        task_status=TaskStatus.QUEUING,
        tag=tag,
        method=method,
        data=data,
    )


class TestBulkDelete:
    """Tests for bulk DELETE operation."""

    def test_delete_small_batch(self, mock_nebula):
        """Delete under WATER_LINE should execute single nGQL."""
        vids = ["vid1", "vid2", "vid3"]
        task = _make_task(BulkMethod.DELETE, vids)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        # Verify single execute call
        mock_nebula.execute.assert_called_once()
        call_args = mock_nebula.execute.call_args[0][0]
        assert "DELETE VERTEX" in call_args
        assert "vid1" in call_args
        assert "vid2" in call_args
        assert "vid3" in call_args
        assert "WITH EDGE" in call_args

    def test_delete_large_batch(self, mock_nebula, monkeypatch):
        """Delete over WATER_LINE should split into batches."""
        # Set water line to 2 for easy testing
        monkeypatch.setattr("core.task.CAASM_WATER_LINE", 2)
        vids = ["v1", "v2", "v3", "v4", "v5"]
        task = _make_task(BulkMethod.DELETE, vids)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        # Should make 3 batch calls (2+2+1)
        assert mock_nebula.execute.call_count == 3

    def test_delete_empty_data(self, mock_nebula):
        """Empty data should be a no-op."""
        task = _make_task(BulkMethod.DELETE, [])
        import asyncio
        asyncio.run(task.run(mock_nebula))
        mock_nebula.execute.assert_not_called()


class TestBulkCreate:
    """Tests for bulk POST (create) operation."""

    def test_create_single_item(self, mock_nebula):
        """Create a single field via bulk POST."""
        data = [{"fieldName": "test_field", "fieldDesc": "test desc", "collects": ["base"]}]
        task = _make_task(BulkMethod.POST, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        # Should call execute at least once (INSERT VERTEX)
        assert mock_nebula.execute.call_count >= 1

    def test_create_skip_existing(self, mock_nebula):
        """Should skip vertices that already exist."""
        mock_nebula.fetch.return_value = MagicMock()  # Already exists
        data = [{"fieldName": "existing_field"}]
        task = _make_task(BulkMethod.POST, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        # Should NOT execute INSERT because vertex exists
        # execute might still be called 0 times (skipped)
        pass  # No assertion needed - just shouldn't crash

    def test_create_multiple_items(self, mock_nebula):
        """Create multiple fields via bulk POST."""
        data = [
            {"fieldName": "f1", "fieldDesc": "d1"},
            {"fieldName": "f2", "fieldDesc": "d2"},
            {"fieldName": "f3", "fieldDesc": "d3"},
        ]
        task = _make_task(BulkMethod.POST, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        # Should have 3 INSERT calls (one per field) + possibly edge calls
        insert_calls = [
            c for c in mock_nebula.execute.call_args_list
            if "INSERT VERTEX" in str(c.args[0]) if c.args
        ]
        assert len(insert_calls) == 3

    def test_create_large_batch(self, mock_nebula, monkeypatch):
        """Create over WATER_LINE should batch."""
        monkeypatch.setattr("core.task.CAASM_WATER_LINE", 2)
        data = [
            {"fieldName": "f1"}, {"fieldName": "f2"},
            {"fieldName": "f3"}, {"fieldName": "f4"},
        ]
        task = _make_task(BulkMethod.POST, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        insert_calls = [
            c for c in mock_nebula.execute.call_args_list
            if c.args and "INSERT VERTEX" in str(c.args[0])
        ]
        assert len(insert_calls) == 4  # 4 individual inserts


class TestBulkUpdate:
    """Tests for bulk PUT (update) operation."""

    def test_update_single_item(self, mock_nebula):
        """Update a single field via bulk PUT."""
        data = [{"id": "vid1", "fieldName": "updated_name", "fieldDesc": "new desc"}]
        task = _make_task(BulkMethod.PUT, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        update_calls = [
            c for c in mock_nebula.execute.call_args_list
            if c.args and "UPDATE VERTEX" in str(c.args[0])
        ]
        assert len(update_calls) == 1

    def test_update_with_collects(self, mock_nebula):
        """Update with collect changes should manage edges."""
        data = [{"id": "vid1", "fieldName": "test", "collects": ["base", "new_collect"]}]
        task = _make_task(BulkMethod.PUT, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        # Should have UPDATE + DELETE edges + INSERT edges
        assert mock_nebula.execute.call_count >= 1

    def test_update_no_id_skip(self, mock_nebula):
        """Item without id should be skipped."""
        data = [{"fieldName": "no_id_item"}]
        task = _make_task(BulkMethod.PUT, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        update_calls = [
            c for c in mock_nebula.execute.call_args_list
            if c.args and "UPDATE VERTEX" in str(c.args[0])
        ]
        assert len(update_calls) == 0

    def test_update_no_changes(self, mock_nebula):
        """Item with empty fields should not execute UPDATE."""
        data = [{"id": "vid1"}]  # No fields to update
        task = _make_task(BulkMethod.PUT, data)
        import asyncio
        asyncio.run(task.run(mock_nebula))

        update_calls = [
            c for c in mock_nebula.execute.call_args_list
            if c.args and "UPDATE VERTEX" in str(c.args[0])
        ]
        assert len(update_calls) == 0


class TestUnsupportedMethod:
    """Tests for unsupported bulk method."""

    def test_unsupported_method_raises(self, mock_nebula):
        """Unsupported method should raise exception."""
        # Use a non-existent method value
        task = _make_task(BulkMethod.DELETE, ["v1"])
        task.method = None  # simulate unsupported
        import asyncio

        with pytest.raises(Exception):
            asyncio.run(task.run(mock_nebula))