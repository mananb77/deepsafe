"""
API Routers

All route handlers for the DeepSafe API.
"""

from src.services.api.routers.health import router as health_router
from src.services.api.routers.auth import router as auth_router
from src.services.api.routers.users import router as users_router
from src.services.api.routers.companies import router as companies_router
from src.services.api.routers.meetings import router as meetings_router
from src.services.api.routers.participants import router as participants_router
from src.services.api.routers.incidents import router as incidents_router
from src.services.api.routers.verifications import router as verifications_router
from src.services.api.routers.policies import router as policies_router
from src.services.api.routers.ws import router as ws_router

__all__ = [
    "health_router",
    "auth_router",
    "users_router",
    "companies_router",
    "meetings_router",
    "participants_router",
    "incidents_router",
    "verifications_router",
    "policies_router",
    "ws_router",
]
