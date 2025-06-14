from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models import User, UserUpdate
from app.database import db
from app.auth import get_current_active_user, get_password_hash

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_active_user)):
    """Get all users (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.read_all("users")
    # Remove passwords from response
    for user in users:
        user.pop("password", None)
    
    return [User(**user) for user in users]

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, current_user: User = Depends(get_current_active_user)):
    """Get user by ID"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.read("users", user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.pop("password", None)
    return User(**user)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if user exists
    existing_user = db.read("users", user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prepare update data
    update_data = user_update.dict(exclude_unset=True)
    
    # Check for email uniqueness if email is being updated
    if "email" in update_data and update_data["email"] != existing_user["email"]:
        existing_email = db.find_one_by_field("users", "email", update_data["email"])
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check for username uniqueness if username is being updated
    if "username" in update_data and update_data["username"] != existing_user["username"]:
        existing_username = db.find_one_by_field("users", "username", update_data["username"])
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user
    updated_user = db.update("users", user_id, update_data)
    updated_user.pop("password", None)
    
    return User(**updated_user)

@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_active_user)):
    """Delete user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = db.delete("users", user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}

@router.get("/profile/me", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    return current_user

@router.put("/profile/me", response_model=User)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile"""
    return await update_user(current_user.id, user_update, current_user) 