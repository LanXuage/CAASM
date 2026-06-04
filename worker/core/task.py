#!/bin/env python3

from enum import Enum
from .log import logger
from abc import abstractmethod
from .nebula import NebulaFacade
from shared.nebula import gen_vid
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake
from typing import List, Any, Optional, Dict
from settings import CAASM_WATER_LINE

# Import shared model definitions
from shared.models.task import (
    BulkMethod,  # noqa: F401 - re-export for backward compatibility
    TaskType,    # noqa: F401
    TaskStatus,  # noqa: F401
    Task as BaseTask,
    BulkTask as BaseBulkTask,
)


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class Task(BaseTask):
    """Worker-side Task with abstract run() method."""

    @abstractmethod
    async def run(self, nebula_facade: NebulaFacade):
        raise NotImplementedError


@dataclass(
    config=ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel, alias=to_snake
        ),
        populate_by_name=True,
        from_attributes=True,
    )
)
class BulkTask(BaseBulkTask, Task):
    """Worker-side BulkTask with concrete run() implementation."""

    async def run(self, nebula_facade: NebulaFacade):
        logger.info("Run bulk task method=%s tag=%s count=%s", self.method, self.tag, len(self.data or []))
        if not self.data:
            logger.info("Empty data, nothing to do")
            return

        if self.method == BulkMethod.DELETE:
            await self._execute_bulk_delete(nebula_facade)
        elif self.method == BulkMethod.POST:
            await self._execute_bulk_create(nebula_facade)
        elif self.method == BulkMethod.PUT:
            await self._execute_bulk_update(nebula_facade)
        else:
            raise Exception("Unsupported bulk method: %s" % self.method)

    # ========== DELETE ==========

    async def _execute_bulk_delete(self, nebula_facade: NebulaFacade):
        """Batch delete vertices. Splits into WATER_LINE-sized batches."""
        if len(self.data) < CAASM_WATER_LINE:
            stmt = 'DELETE VERTEX "{}" WITH EDGE'.format('","'.join(self.data))
            logger.info("Delete nGQL: %s...", stmt[:100])
            result = nebula_facade.execute(stmt)
            assert result.is_succeeded(), "Execute nGQL failed"
        else:
            await self._batch_execute(nebula_facade, self.data, self._delete_batch, "delete")

    async def _delete_batch(self, nebula_facade: NebulaFacade, batch: List[str]):
        stmt = 'DELETE VERTEX "{}" WITH EDGE'.format('","'.join(batch))
        result = nebula_facade.execute(stmt)
        assert result.is_succeeded(), "Execute nGQL failed"

    # ========== POST (batch create) ==========

    async def _execute_bulk_create(self, nebula_facade: NebulaFacade):
        """Batch create vertices. Each item is a dict with field properties."""

        async def _create_batch(nebula_facade: NebulaFacade, batch: List[Any]):
            for item in batch:
                await self._create_single_vertex(nebula_facade, item)

        if len(self.data) < CAASM_WATER_LINE:
            async def _create_batch(nebula_facade, batch):
                for item in batch:
                    await self._create_single_vertex(nebula_facade, item)
            await _create_batch(nebula_facade, self.data)
        else:
            await self._batch_execute(nebula_facade, self.data, _create_batch, "create")

    async def _create_single_vertex(self, nebula_facade: NebulaFacade, item: Any):
        """Create a single vertex from a data item."""
        tag = self.tag or "field"
        if isinstance(item, dict):
            field_name = item.get("fieldName") or item.get("field_name") or ""
            field_desc = item.get("fieldDesc") or item.get("field_desc") or ""
            collects = item.get("collects") or []
        else:
            field_name = str(item)
            field_desc = ""
            collects = []

        vid = gen_vid(tag, field_name)

        # Skip if already exists
        existing = nebula_facade.fetch(tag, vid)
        if existing is not None:
            logger.info("Vertex %s already exists, skipping", vid)
            return

        stmt = 'INSERT VERTEX IF NOT EXISTS {}(field_name, field_desc) VALUES "{}":($field_name, $field_desc)'.format(
            tag, vid
        )
        result = nebula_facade.execute(stmt, field_name=field_name, field_desc=field_desc)
        assert result.is_succeeded(), "server_err"

        # Create edge relationships for field_collect
        if collects:
            edge_stmt = "INSERT EDGE IF NOT EXISTS field_e_collect() VALUES "
            for c in collects:
                collect_name = c if isinstance(c, str) else c.get("collectName", "")
                edge_stmt += '"{}"->"{}":(),'.format(vid, gen_vid("field_collect", collect_name))
            nebula_facade.execute(edge_stmt[:-1])

    # ========== PUT (batch update) ==========

    async def _execute_bulk_update(self, nebula_facade: NebulaFacade):
        """Batch update vertices. Each item is a dict with id and updated fields."""

        async def _update_batch(nebula_facade: NebulaFacade, batch: List[Any]):
            for item in batch:
                await self._update_single_vertex(nebula_facade, item)

        if len(self.data) < CAASM_WATER_LINE:
            await _update_batch(nebula_facade, self.data)
        else:
            await self._batch_execute(nebula_facade, self.data, _update_batch, "update")

    async def _update_single_vertex(self, nebula_facade: NebulaFacade, item: Any):
        """Update a single vertex from a data item."""
        tag = self.tag or "field"

        if isinstance(item, dict):
            vid = item.get("id") or ""
            field_name = item.get("fieldName") or item.get("field_name")
            field_desc = item.get("fieldDesc") or item.get("field_desc")
            collects = item.get("collects")
        else:
            return  # Can't update without an id

        if not vid:
            logger.warning("No id in update item, skipping")
            return

        # Update vertex properties
        set_parts = []
        params = {}
        if field_name is not None:
            set_parts.append("field_name=$field_name")
            params["field_name"] = field_name
        if field_desc is not None:
            set_parts.append("field_desc=$field_desc")
            params["field_desc"] = field_desc

        if set_parts:
            set_parts.append("updated_at=now()")
            stmt = 'UPDATE VERTEX ON {} "{}" SET {}'.format(tag, vid, ", ".join(set_parts))
            result = nebula_facade.execute(stmt, **params)
            assert result.is_succeeded(), "server_err"

        # Update edge relationships
        if collects is not None:
            del_stmt = (
                'GO FROM "{}" OVER field_e_collect '
                "YIELD src(edge) AS src, dst(edge) AS dst, rank(edge) AS rank "
                "| DELETE EDGE field_e_collect $-.src -> $-.dst @ $-.rank"
            ).format(vid)
            nebula_facade.execute(del_stmt)

            if collects:
                edge_stmt = "INSERT EDGE IF NOT EXISTS field_e_collect() VALUES "
                for c in collects:
                    collect_name = c if isinstance(c, str) else c.get("collectName", "")
                    edge_stmt += '"{}"->"{}":(),'.format(vid, gen_vid("field_collect", collect_name))
                nebula_facade.execute(edge_stmt[:-1])

    # ========== Batch execution helper ==========

    async def _batch_execute(
        self,
        nebula_facade: NebulaFacade,
        data: List[Any],
        batch_handler,
        operation: str,
    ):
        """Split data into WATER_LINE-sized batches and execute handler."""
        batch_size = CAASM_WATER_LINE
        total = len(data)
        for i in range(0, total, batch_size):
            batch = data[i : i + batch_size]
            logger.info(
                "Batch %s [%s/%s] processing %s items",
                operation,
                min(i + batch_size, total),
                total,
                len(batch),
            )
            await batch_handler(nebula_facade, batch)
        logger.info("Batch %s completed: %s items", operation, total)