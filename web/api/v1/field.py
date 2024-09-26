#!/bin/env python3
import csv
import model

from common.app import App
from common.log import logger
from common.nebula import make_object, gen_vid
from deps.permission import PermissionChecker
from fastapi import APIRouter, Request, Depends
from nebula3.common.ttypes import Row, Value, NList, Vertex

field_router = APIRouter()
field_tag = "field"


@field_router.post(path="/field", response_model=model.Response)
def add_field(
    req: Request,
    field: model.Field,
    _: bool = Depends(PermissionChecker(["field_create_permission"])),
) -> model.Response:
    app: App = req.app
    vid = gen_vid(field_tag, field.field_name)
    assert not app.nebula_facade.fetch(field_tag, vid), "field_exist"
    stmt = 'INSERT VERTEX IF NOT EXISTS {}(field_name, field_desc) VALUES "{}":($field_name, $field_desc)'.format(
        field_tag, vid
    )
    result = app.nebula_facade.execute(
        stmt, field_name=field.field_name, field_desc=field.field_desc
    )
    assert result.is_succeeded(), "server_err"
    stmt = "INSERT EDGE IF NOT EXISTS field_e_collect() VALUES "
    for collect in field.collects:
        stmt += '"{}"->"{}":(),'.format(vid, gen_vid("field_collect", collect))
    result = app.nebula_facade.execute(stmt[:-1])
    assert result.is_succeeded(), "server_err"
    v = app.nebula_facade.fetch(field_tag, vid)
    assert isinstance(v, Vertex), "server_err"
    return model.Response(data=make_object(model.Field, v, collects=field.collects))


@field_router.delete(path="/field/{vid}", response_model=model.Response)
def del_field(
    req: Request,
    vid: str,
    _: bool = Depends(PermissionChecker(["field_modify_permission"])),
):
    app: App = req.app
    stmt = 'DELETE VERTEX "{}" WITH EDGE'.format(vid)
    result = app.nebula_facade.execute(stmt)
    return model.Response(data=result.is_succeeded())


async def process_bulk_file(app: App, fname: str):
    fpath = app.file_manager.get_path(fname)
    if fpath.endswith(".csv"):
        with open(fpath, newline="") as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                pass
                


@field_router.post(path="/fields/bulk", response_model=model.Response)
async def bulk_field(
    req: Request,
    bulk: model.Bulk,
    _: bool = Depends(PermissionChecker(["field_modify_permission"])),
):
    app: App = req.app
    logger.info("bulk method %s", bulk.method)
    if bulk.method == "DELETE":
        stmt = 'DELETE VERTEX "'
        for vid in bulk.data:
            stmt += vid + '","'
        stmt = stmt[:-2] + " WITH EDGE"
        logger.info("stmt %s", stmt)
        result = app.nebula_facade.execute(stmt)
        return model.Response(data=result.is_succeeded())
    elif bulk.method == "POST":
        logger.info("bulk_data is %s", bulk.data)
        if isinstance(bulk.data, str):
            await process_bulk_file(app, bulk.data)
        elif isinstance(bulk.data, list):
            for fname in bulk.data:
                await process_bulk_file(app, fname)
        return model.Response(data=True)
    else:
        raise Exception("unsupport_method")


@field_router.put(path="/field/{vid}", response_model=model.Response)
def modify_field(
    req: Request,
    vid: str,
    field: model.Field,
    _: bool = Depends(PermissionChecker(["field_modify_permission"])),
):
    app: App = req.app
    stmt = 'UPDATE VERTEX ON {} "{}" SET field_name=$field_name, field_desc=$field_desc, updated_at=now()'.format(
        field_tag, vid
    )
    result = app.nebula_facade.execute(
        stmt, field_name=field.field_name, field_desc=field.field_desc
    )
    assert result.is_succeeded(), "server_err"
    stmt = 'GO FROM "{}" OVER field_e_collect \
        YIELD src(edge) AS src, dst(edge) AS dst, rank(edge) AS rank \
        | DELETE EDGE field_e_collect $-.src -> $-.dst @ $-.rank'.format(
        vid
    )
    result = app.nebula_facade.execute(stmt)
    assert result.is_succeeded(), "server_err"
    stmt = "INSERT EDGE IF NOT EXISTS field_e_collect() VALUES "
    for collect in field.collects:
        stmt += '"{}"->"{}":(),'.format(vid, gen_vid("field_collect", collect))
    result = app.nebula_facade.execute(stmt[:-1])
    assert result.is_succeeded(), "server_err"
    v = app.nebula_facade.fetch(field_tag, vid)
    assert isinstance(v, Vertex), "server_err"
    return model.Response(data=make_object(model.Field, v, collects=field.collects))


@field_router.get(path="/fields", response_model=model.Response)
def get_fields(req: Request) -> model.Response:
    app: App = req.app
    stmt = """LOOKUP ON {} YIELD VERTEX AS v, id(VERTEX) AS id \
        | GO FROM $-.id OVER field_e_collect YIELD $-.v AS v, $$.field_collect.collect_name AS collect_name \
        | GROUP BY $-.v YIELD $-.v AS v, collect($-.collect_name) AS collect_names""".format(
        field_tag
    )
    result = app.nebula_facade.execute(stmt)
    fields = []
    for row in result.rows():
        assert isinstance(row, Row), "server_err"
        assert isinstance(row.values[0], Value), "server_err"
        assert isinstance(row.values[1], Value), "server_err"
        v = row.values[0].get_vVal()
        assert isinstance(v, Vertex), "server_err"
        collects = row.values[1].get_lVal()
        assert isinstance(collects, NList), "server_err"
        fields.append(
            make_object(
                model.Field,
                v,
                collects=[c.get_sVal().decode() for c in collects.values],
            )
        )
    return model.Response(data=fields)
