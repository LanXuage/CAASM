#!/bin/env python

from common.log import logger
from datetime import datetime
from nebula3.common.ttypes import Value
from typing import Type, Any, Dict, Optional, TypeVar

T = TypeVar("T")

def make_object(model: Type[T], props: Dict[bytes, Value], id: Optional[str] = None) -> T:
    annotations = model.__annotations__
    logger.info("annotations %s", annotations)
    params: Dict[str, Any] = {}
    if "id" in annotations.keys() and id is not None:
        params["id"] = id
    for k, v in props.items():
        attr_key = k.decode()
        logger.info("attr_key %s", attr_key)
        if attr_key in annotations.keys():
            t = annotations.get(attr_key)
            if t == int:
                params[attr_key] = v.value
            elif t == str:
                assert isinstance(v.value, bytes), "model_mismatch"
                params[attr_key] = v.value.decode()
            elif t == datetime:
                assert isinstance(v.value, int), "model_mismatch"
                params[attr_key] = datetime.fromtimestamp(v.value)
            else:
                logger.warning("type not match %s - %s", attr_key, t)
    logger.info("params %s", params)
    return model(**params)
