#!/bin/env python3
"""
Permission management CRUD API endpoints.

Provides:
- List / Create / Get / Update / Delete permissions
- Permission include (parent-child) relationships
- Permission group management
"""

import model

from common.app import App
from common.log import logger
from common.nebula import make_object, gen_vid
from typing import List, Optional
from deps.permission import PermissionChecker
from fastapi import APIRouter, Request, Depends
from nebula3.common.ttypes import Row, Value, Vertex

perm_router = APIRouter()
PERM_TAG = "caasm_perm"
PERM_GROUP_TAG = "caasm_perm_group"


# ========== Permission CRUD ==========


@perm_router.get(path="/perms", response_model=model.Response)
async def list_perms(
    req: Request,
    _: bool = Depends(PermissionChecker(["perm_read_permission"])),
) -> model.Response:
    """List all permissions."""
    app: App = req.app
    stmt = "LOOKUP ON {} YIELD VERTEX AS v".format(PERM_TAG)
    result = app.nebula_facade.execute(stmt)
    perms: List[model.Perm] = []
    for row in result.rows():
        if isinstance(row, Row) and row.values:
            vertex = row.values[0].get_vVal()
            if isinstance(vertex, Vertex):
                perms.append(make_object(model.Perm, vertex))
    return model.Response(data=perms)


@perm_router.post(path="/perm", response_model=model.Response)
async def create_perm(
    req: Request,
    perm_create: model.PermCreate,
    _: bool = Depends(PermissionChecker(["perm_create_permission"])),
) -> model.Response:
    """Create a new permission."""
    app: App = req.app
    vid = gen_vid(PERM_TAG, perm_create.perm_name)

    existing = app.nebula_facade.fetch(PERM_TAG, vid)
    assert existing is None, "perm_exist"

    stmt = (
        'INSERT VERTEX IF NOT EXISTS {}(perm_name, perm_desc) '
        'VALUES "{}":($perm_name, $perm_desc)'
    ).format(PERM_TAG, vid)
    result = app.nebula_facade.execute(
        stmt, perm_name=perm_create.perm_name, perm_desc=perm_create.perm_desc,
    )
    assert result.is_succeeded(), "server_err"

    # Link to permission group if specified
    if perm_create.perm_group_id:
        edge_stmt = 'INSERT EDGE IF NOT EXISTS perm_e_group() VALUES "{}"->"{}":()'.format(
            vid, perm_create.perm_group_id
        )
        app.nebula_facade.execute(edge_stmt)

    vertex = app.nebula_facade.fetch(PERM_TAG, vid)
    assert isinstance(vertex, Vertex), "server_err"
    return model.Response(data=make_object(model.Perm, vertex))


@perm_router.get(path="/perm/{perm_id}", response_model=model.Response)
async def get_perm(
    req: Request,
    perm_id: str,
    _: bool = Depends(PermissionChecker(["perm_read_permission"])),
) -> model.Response:
    """Get permission details."""
    app: App = req.app

    vertex = app.nebula_facade.fetch(PERM_TAG, perm_id)
    assert isinstance(vertex, Vertex), "perm_not_found"

    return model.Response(data=make_object(model.Perm, vertex))


@perm_router.put(path="/perm/{perm_id}", response_model=model.Response)
async def update_perm(
    req: Request,
    perm_id: str,
    perm_update: model.PermUpdate,
    _: bool = Depends(PermissionChecker(["perm_modify_permission"])),
) -> model.Response:
    """Update permission information."""
    app: App = req.app

    set_parts = []
    params = {}
    if perm_update.perm_name is not None:
        set_parts.append("perm_name=$perm_name")
        params["perm_name"] = perm_update.perm_name
    if perm_update.perm_desc is not None:
        set_parts.append("perm_desc=$perm_desc")
        params["perm_desc"] = perm_update.perm_desc

    if not set_parts:
        return model.Response(data="no_fields_to_update")

    set_parts.append("updated_at=now()")
    stmt = 'UPDATE VERTEX ON {} "{}" SET {}'.format(PERM_TAG, perm_id, ", ".join(set_parts))
    result = app.nebula_facade.execute(stmt, **params)
    assert result.is_succeeded(), "server_err"

    return model.Response(data="updated")


@perm_router.delete(path="/perm/{perm_id}", response_model=model.Response)
async def delete_perm(
    req: Request,
    perm_id: str,
    _: bool = Depends(PermissionChecker(["perm_modify_permission"])),
) -> model.Response:
    """Delete a permission and all associated edges."""
    app: App = req.app
    stmt = 'DELETE VERTEX "{}" WITH EDGE'.format(perm_id)
    result = app.nebula_facade.execute(stmt)
    assert result.is_succeeded(), "server_err"
    return model.Response(data="deleted")


# ========== Permission include relationship ==========


@perm_router.post(path="/perm/{perm_id}/include", response_model=model.Response)
async def set_perm_include(
    req: Request,
    perm_id: str,
    include: model.PermInclude,
    _: bool = Depends(PermissionChecker(["perm_modify_permission"])),
) -> model.Response:
    """Set permission include relationship (parent includes child)."""
    app: App = req.app

    insert_stmt = 'INSERT EDGE IF NOT EXISTS perm_include() VALUES "{}"->"{}":()'.format(
        perm_id, include.child_perm_id
    )
    result = app.nebula_facade.execute(insert_stmt)
    assert result.is_succeeded(), "server_err"

    return model.Response(data="include_set")


# ========== Permission group management ==========


@perm_router.get(path="/perm-groups", response_model=model.Response)
async def list_perm_groups(
    req: Request,
    _: bool = Depends(PermissionChecker(["perm_read_permission"])),
) -> model.Response:
    """List all permission groups."""
    app: App = req.app
    stmt = "LOOKUP ON {} YIELD VERTEX AS v".format(PERM_GROUP_TAG)
    result = app.nebula_facade.execute(stmt)
    groups: List[model.PermGroup] = []
    for row in result.rows():
        if isinstance(row, Row) and row.values:
            vertex = row.values[0].get_vVal()
            if isinstance(vertex, Vertex):
                groups.append(make_object(model.PermGroup, vertex))
    return model.Response(data=groups)


@perm_router.post(path="/perm-group", response_model=model.Response)
async def create_perm_group(
    req: Request,
    group_create: model.PermGroupCreate,
    _: bool = Depends(PermissionChecker(["perm_create_permission"])),
) -> model.Response:
    """Create a new permission group."""
    app: App = req.app
    vid = gen_vid(PERM_GROUP_TAG, group_create.perm_group_name)

    existing = app.nebula_facade.fetch(PERM_GROUP_TAG, vid)
    assert existing is None, "perm_group_exist"

    stmt = (
        'INSERT VERTEX IF NOT EXISTS {}(perm_group_name, perm_group_desc) '
        'VALUES "{}":($perm_group_name, $perm_group_desc)'
    ).format(PERM_GROUP_TAG, vid)
    result = app.nebula_facade.execute(
        stmt,
        perm_group_name=group_create.perm_group_name,
        perm_group_desc=group_create.perm_group_desc,
    )
    assert result.is_succeeded(), "server_err"

    vertex = app.nebula_facade.fetch(PERM_GROUP_TAG, vid)
    assert isinstance(vertex, Vertex), "server_err"
    return model.Response(data=make_object(model.PermGroup, vertex))