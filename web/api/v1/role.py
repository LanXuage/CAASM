#!/bin/env python3
"""
Role management CRUD API endpoints.

Provides:
- List / Create / Get / Update / Delete roles
- Assign permissions to roles
- Assign users to roles
- Role inheritance and mutual exclusion
"""

import model
import time

from common.app import App
from common.log import logger
from common.nebula import make_object, gen_vid
from typing import List, Optional
from deps.permission import PermissionChecker
from fastapi import APIRouter, Request, Depends
from nebula3.common.ttypes import Row, Value, Vertex

role_router = APIRouter()
ROLE_TAG = "caasm_role"


# ========== Helper functions ==========

def _fetch_related_ids(app: App, vid: str, edge: str, direction: str = "out") -> List[str]:
    """Fetch related vertex IDs via an edge."""
    if direction == "out":
        stmt = 'GO FROM "{}" OVER {} YIELD dst(edge) AS target_id'.format(vid, edge)
    else:
        stmt = 'GO FROM "{}" OVER {} REVERSELY YIELD src(edge) AS target_id'.format(vid, edge)
    result = app.nebula_facade.execute(stmt)
    ids: List[str] = []
    if result.is_succeeded():
        for row in result.rows():
            if row.values and row.values[0]:
                val = row.values[0].get_sVal()
                ids.append(val.decode() if isinstance(val, bytes) else val)
    return ids


# ========== CRUD endpoints ==========


@role_router.get(path="/roles", response_model=model.Response)
async def list_roles(
    req: Request,
    _: bool = Depends(PermissionChecker(["role_read_permission"])),
) -> model.Response:
    """List all roles."""
    app: App = req.app
    stmt = "LOOKUP ON {} YIELD VERTEX AS v".format(ROLE_TAG)
    result = app.nebula_facade.execute(stmt)
    roles: List[model.Role] = []
    for row in result.rows():
        if isinstance(row, Row) and row.values:
            vertex = row.values[0].get_vVal()
            if isinstance(vertex, Vertex):
                roles.append(make_object(model.Role, vertex))
    return model.Response(data=roles)


@role_router.post(path="/role", response_model=model.Response)
async def create_role(
    req: Request,
    role_create: model.RoleCreate,
    _: bool = Depends(PermissionChecker(["role_create_permission"])),
) -> model.Response:
    """Create a new role."""
    app: App = req.app
    vid = gen_vid(ROLE_TAG, role_create.role_name)

    existing = app.nebula_facade.fetch(ROLE_TAG, vid)
    assert existing is None, "role_exist"

    stmt = (
        'INSERT VERTEX IF NOT EXISTS {}(role_name, role_desc) '
        'VALUES "{}":($role_name, $role_desc)'
    ).format(ROLE_TAG, vid)
    result = app.nebula_facade.execute(
        stmt, role_name=role_create.role_name, role_desc=role_create.role_desc,
    )
    assert result.is_succeeded(), "server_err"

    vertex = app.nebula_facade.fetch(ROLE_TAG, vid)
    assert isinstance(vertex, Vertex), "server_err"
    return model.Response(data=make_object(model.Role, vertex))


@role_router.get(path="/role/{role_id}", response_model=model.Response)
async def get_role(
    req: Request,
    role_id: str,
    _: bool = Depends(PermissionChecker(["role_read_permission"])),
) -> model.Response:
    """Get role details with associated permissions and users."""
    app: App = req.app

    vertex = app.nebula_facade.fetch(ROLE_TAG, role_id)
    assert isinstance(vertex, Vertex), "role_not_found"

    perm_ids = _fetch_related_ids(app, role_id, "perm_e_role", "in")
    user_ids = _fetch_related_ids(app, role_id, "user_e_role", "in")

    return model.Response(
        data=make_object(model.RoleDetail, vertex, perm_ids=perm_ids, user_ids=user_ids)
    )


@role_router.put(path="/role/{role_id}", response_model=model.Response)
async def update_role(
    req: Request,
    role_id: str,
    role_update: model.RoleUpdate,
    _: bool = Depends(PermissionChecker(["role_modify_permission"])),
) -> model.Response:
    """Update role information."""
    app: App = req.app

    set_parts = []
    params = {}
    if role_update.role_name is not None:
        set_parts.append("role_name=$role_name")
        params["role_name"] = role_update.role_name
    if role_update.role_desc is not None:
        set_parts.append("role_desc=$role_desc")
        params["role_desc"] = role_update.role_desc

    if not set_parts:
        return model.Response(data="no_fields_to_update")

    set_parts.append("updated_at=now()")
    stmt = 'UPDATE VERTEX ON {} "{}" SET {}'.format(ROLE_TAG, role_id, ", ".join(set_parts))
    result = app.nebula_facade.execute(stmt, **params)
    assert result.is_succeeded(), "server_err"

    return model.Response(data="updated")


@role_router.delete(path="/role/{role_id}", response_model=model.Response)
async def delete_role(
    req: Request,
    role_id: str,
    _: bool = Depends(PermissionChecker(["role_modify_permission"])),
) -> model.Response:
    """Delete a role and all associated edges."""
    app: App = req.app
    stmt = 'DELETE VERTEX "{}" WITH EDGE'.format(role_id)
    result = app.nebula_facade.execute(stmt)
    assert result.is_succeeded(), "server_err"
    return model.Response(data="deleted")


# ========== Relationship endpoints ==========


@role_router.post(path="/role/{role_id}/perms", response_model=model.Response)
async def assign_role_perms(
    req: Request,
    role_id: str,
    perm_assign: model.RoleAssignPerms,
    _: bool = Depends(PermissionChecker(["role_modify_permission"])),
) -> model.Response:
    """Assign permissions to a role. Replaces existing assignments."""
    app: App = req.app

    # Delete existing permission assignments
    del_stmt = (
        'GO FROM "{}" OVER perm_e_role REVERSELY '
        "YIELD src(edge) AS src, rank(edge) AS rank "
        "| DELETE EDGE perm_e_role $-.src -> $-.dst @ $-.rank"
    ).format(role_id)
    app.nebula_facade.execute(del_stmt)

    # Insert new permission assignments
    if perm_assign.perm_ids:
        insert_stmt = "INSERT EDGE IF NOT EXISTS perm_e_role() VALUES "
        for perm_id in perm_assign.perm_ids:
            insert_stmt += '"{}"->"{}":(),'.format(perm_id, role_id)
        result = app.nebula_facade.execute(insert_stmt[:-1])
        assert result.is_succeeded(), "server_err"

    return model.Response(data="perms_assigned")


@role_router.post(path="/role/{role_id}/users", response_model=model.Response)
async def assign_role_users(
    req: Request,
    role_id: str,
    user_assign: model.RoleAssignUsers,
    _: bool = Depends(PermissionChecker(["role_modify_permission"])),
) -> model.Response:
    """Assign users to a role. Replaces existing assignments."""
    app: App = req.app

    # Delete existing user assignments
    del_stmt = (
        'GO FROM "{}" OVER user_e_role REVERSELY '
        "YIELD src(edge) AS src, rank(edge) AS rank "
        "| DELETE EDGE user_e_role $-.src -> $-.dst @ $-.rank"
    ).format(role_id)
    app.nebula_facade.execute(del_stmt)

    # Insert new user assignments
    if user_assign.user_ids:
        insert_stmt = "INSERT EDGE IF NOT EXISTS user_e_role() VALUES "
        for user_id in user_assign.user_ids:
            insert_stmt += '"{}"->"{}":(),'.format(user_id, role_id)
        result = app.nebula_facade.execute(insert_stmt[:-1])
        assert result.is_succeeded(), "server_err"

    return model.Response(data="users_assigned")


@role_router.post(path="/role/{role_id}/inherit", response_model=model.Response)
async def set_role_inherit(
    req: Request,
    role_id: str,
    inherit: model.RoleInherit,
    _: bool = Depends(PermissionChecker(["role_modify_permission"])),
) -> model.Response:
    """Set role inheritance (this role inherits from parent_role_id)."""
    app: App = req.app

    # Delete existing inheritance from this role
    del_stmt = (
        'GO FROM "{}" OVER role_inherit '
        "YIELD src(edge) AS src, dst(edge) AS dst, rank(edge) AS rank "
        "| DELETE EDGE role_inherit $-.src -> $-.dst @ $-.rank"
    ).format(role_id)
    app.nebula_facade.execute(del_stmt)

    # Insert new inheritance
    insert_stmt = 'INSERT EDGE IF NOT EXISTS role_inherit() VALUES "{}"->"{}":()'.format(
        role_id, inherit.parent_role_id
    )
    result = app.nebula_facade.execute(insert_stmt)
    assert result.is_succeeded(), "server_err"

    return model.Response(data="inherit_set")


@role_router.post(path="/role/{role_id}/mutex", response_model=model.Response)
async def set_role_mutex(
    req: Request,
    role_id: str,
    mutex: model.RoleMutex,
    _: bool = Depends(PermissionChecker(["role_modify_permission"])),
) -> model.Response:
    """Set mutual exclusion between two roles."""
    app: App = req.app

    # Insert mutual exclusion (bidirectional - both edges)
    insert_stmt = (
        'INSERT EDGE IF NOT EXISTS role_mutex() '
        'VALUES "{}"->"{}":(), "{}"->"{}":()'
    ).format(role_id, mutex.mutex_role_id, mutex.mutex_role_id, role_id)
    result = app.nebula_facade.execute(insert_stmt)
    assert result.is_succeeded(), "server_err"

    return model.Response(data="mutex_set")