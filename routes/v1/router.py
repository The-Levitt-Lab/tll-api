from fastapi import APIRouter

from .endpoints.admin import router as admin_router
from .endpoints.auth import router as auth_router
from .endpoints.health import router as health_router
from .endpoints.users import router as users_router


api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

