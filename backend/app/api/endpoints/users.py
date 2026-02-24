from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_premium_user, get_current_admin_user
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserUpdate, PasswordChangeRequest, UserCreate

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update current user's profile info"""
    if user_in.email is not None:
        # Check if email taken
        res = await db.execute(select(User).where(User.email == user_in.email, User.id != current_user.id))
        if res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_in.email
    
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
        
    # Standard users cannot change their own Role or Active status
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/me/change-password")
async def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Securely change user's password"""
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
    
    current_user.password_hash = get_password_hash(req.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Đổi mật khẩu thành công"}


# --- ADMIN ONLY ROUTES ---

@router.post("/", response_model=UserOut)
async def create_user_admin(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> Any:
    """Create new user (Admin only)"""
    # Check if email taken
    res = await db.execute(select(User).where(User.email == user_in.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> Any:
    """List all users (Admin only)"""
    result = await db.execute(select(User).offset(skip).limit(limit).order_by(User.id))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> Any:
    """Get specific user by ID (Admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> Any:
    """Update user by ID (Admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Special handling for password
    if "password" in update_data:
        user.password_hash = get_password_hash(update_data.pop("password"))
        
    for field, value in update_data.items():
        setattr(user, field, value)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
) -> Any:
    """Delete user (Admin only)"""
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
