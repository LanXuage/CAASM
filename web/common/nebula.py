#!/bin/env python
import hashlib

from common.datetime import ZONE_INFO
from enum import Enum
from common.log import logger
from datetime import datetime
from nebula3.common.ttypes import Vertex, Tag, Row, Value
from nebula3.data.ResultSet import ResultSet
from nebula3.gclient.net.SessionPool import SessionPool
from nebula3.Config import SessionPoolConfig
from typing import Type, Any, Dict, TypeVar, List, Tuple, Optional, Union

T = TypeVar("T")


def gen_vid(tag: str, *argv: str) -> str:
    return hashlib.md5("_".join((tag,) + argv).encode()).hexdigest()


def expand_enum(data: Dict[str, Any]) -> Dict[str, Any]:
    for k in data.keys():
        v = data[k]
        if isinstance(v, Enum):
            data[k] = v.value
    return data


def make_object(model: Type[T], vertex: Vertex, **kwargv: Any) -> T:
    annotations = model.__annotations__
    logger.info("annotations %s", annotations)
    params: Dict[str, Any] = {}
    if "id" in annotations.keys():
        params["id"] = vertex.vid.get_sVal()
    assert isinstance(vertex.tags[0], Tag), "model_mismatch"
    for k, v in vertex.tags[0].props.items():
        attr_key = k.decode() if isinstance(k, bytes) else str(k)
        logger.info("attr_key %s", attr_key)
        if attr_key in annotations.keys():
            t = annotations.get(attr_key)
            assert isinstance(v, Value), "model_mismatch"
            if (t == int or t == Optional[int]) and isinstance(v.value, int):
                params[attr_key] = v.value
            elif (t == str or t == Optional[str]) and isinstance(v.value, bytes):
                params[attr_key] = v.value.decode()
            elif (t == datetime or t == Optional[datetime]) and isinstance(
                v.value, int
            ):
                params[attr_key] = datetime.fromtimestamp(v.value, tz=ZONE_INFO)
            else:
                logger.warning("type not match %s - %s", attr_key, t)
    for k, v in kwargv.items():
        if k in annotations.keys():
            params[k] = v
    logger.info("params %s", params)
    return model(**params)


class NebulaFacade:
    def __init__(
        self,
        username: str,
        password: str,
        space_name: str,
        addresses: List[Tuple[str, Union[int, str]]],
        session_pool_config: SessionPoolConfig = SessionPoolConfig(),
    ) -> None:
        self.nebula_session_pool = SessionPool(
            username, password, space_name, addresses
        )
        self.nebula_session_pool.init(session_pool_config)

    def fetch(self, tag: str, vid: str) -> Optional[Vertex]:
        stmt = 'FETCH PROP ON {} "{}" YIELD VERTEX AS v'.format(tag, vid)
        result_set = self.execute(stmt)
        if result_set.row_size() < 1:
            return None
        rows = result_set.rows()
        if (
            not isinstance(rows, list)
            or not isinstance(rows[0], Row)
            or len(rows[0].values) < 1
        ):
            return None
        values = rows[0].values
        if not isinstance(values[0], Value):
            return None
        vertex = values[0].get_vVal()
        return vertex if isinstance(vertex, Vertex) else None

    def execute(self, stmt: str, **kwargv: Any) -> ResultSet:
        return self.nebula_session_pool.execute_py(stmt, expand_enum(kwargv))

    def insert(self, tag: str, obj: Any) -> bool:
        return True

    def close(self):
        self.nebula_session_pool.close()
