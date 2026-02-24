from fastapi import APIRouter

from app.api.endpoints import auth, users, crawler, stats, predictions, favorites

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(favorites.router, prefix="/users/favorites", tags=["favorites"])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
