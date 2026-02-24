from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.core.database import async_session
from app.models.user_favorite import UserFavorite
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

class FavoriteCreate(BaseModel):
    favorite_numbers: list[int] = Field(..., min_items=6, max_items=6, description="Exactly 6 unique numbers (1-45)")

@router.get("")
async def get_my_favorites(current_user: User = Depends(get_current_user)):
    """Retrieve the current logged-in user's favorite numbers."""
    async with async_session() as db:
        result = await db.execute(select(UserFavorite).where(UserFavorite.user_id == current_user.id))
        fav = result.scalar_one_or_none()
        
        if not fav:
            return {"favorite_numbers": [], "notification_enabled": False}
        return {"favorite_numbers": fav.favorite_numbers, "notification_enabled": fav.notification_enabled}

@router.post("")
async def save_my_favorites(data: FavoriteCreate, current_user: User = Depends(get_current_user)):
    """Set or update the user's favorite numbers."""
    
    unique_nums = set(data.favorite_numbers)
    if len(unique_nums) != 6 or any(n < 1 or n > 45 for n in unique_nums):
        raise HTTPException(status_code=400, detail="Must provide exactly 6 unique numbers between 1 and 45.")
        
    async with async_session() as db:
        result = await db.execute(select(UserFavorite).where(UserFavorite.user_id == current_user.id))
        fav = result.scalar_one_or_none()
        
        if fav:
            fav.favorite_numbers = list(unique_nums)
        else:
            new_fav = UserFavorite(user_id=current_user.id, favorite_numbers=list(unique_nums))
            db.add(new_fav)
            
        await db.commit()
        return {"message": "Favorite sequence saved successfully.", "numbers": list(unique_nums)}
