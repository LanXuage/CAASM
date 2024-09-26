from fastapi import APIRouter

from .user import user_router
from .common import common_router
from .field import field_router
from .field_collect import field_collect_router

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(user_router)
v1_router.include_router(common_router)
v1_router.include_router(field_router)
v1_router.include_router(field_collect_router)