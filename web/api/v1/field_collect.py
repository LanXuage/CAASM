#!/bin/env python3
import model

from common.app import App
from common.log import logger
from common.nebula import make_object
from typing import List
from deps.permission import PermissionChecker
from fastapi import APIRouter, Request, Depends
from nebula3.common.ttypes import Row, Value, Vertex

field_collect_router = APIRouter()


@field_collect_router.get(path="/field-collects", response_model=model.Response)
def get_field_collects(
    req: Request,
    _: bool = Depends(PermissionChecker(["field_collect_read_permission"])),
):
    app: App = req.app
    ngql = """LOOKUP ON field_collect YIELD VERTEX AS v"""
    result = app.nebula_facade.execute(ngql)
    ret: List[model.FieldCollect] = []
    for row in result.rows():
        assert (
            isinstance(row, Row)
            and isinstance(row.values[0], Value)
            and isinstance(row.values[0].value, Vertex)
        ), "server_err"
        ret.append(make_object(model.FieldCollect, row.values[0].value))
    return model.Response(data=ret)
