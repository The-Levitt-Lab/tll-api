from fastapi import APIRouter

from .endpoints.admin import router as admin_router
from .endpoints.auth import router as auth_router
from .endpoints.health import router as health_router
from .endpoints.users import router as users_router
from .endpoints.requests import router as requests_router
from .endpoints.transactions import router as transactions_router
from .endpoints.shop import router as shop_router
from .endpoints.challenges import router as challenges_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(requests_router, prefix="/requests", tags=["requests"])
api_router.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
api_router.include_router(shop_router, prefix="/shop", tags=["shop"])
api_router.include_router(challenges_router, prefix="/challenges", tags=["challenges"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
