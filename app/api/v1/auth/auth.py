from fastapi import APIRouter, Depends, HTTPException, status,Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from db.session import get_db
from api.v1.auth.models import User
from api.v1.auth.schemas import UserCreate,UserRead, PasswordReset, PasswordReset_by_admin
from api.v1.auth.user import user_crud
from api.v1.auth.dependencies import admin_required,get_current_active_user
from api.v1.auth.security import create_access_token
from api.v1.auth.security import verify_password
from core.config import settings
from api.v1.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_admin(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),

):
    """Admin-only route to register new users (with any role)"""
    existing_user = await user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    return await user_crud.create_user(db, user_data)

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(admin_required)
):
    """
    Admin creates a new user with a specified role.
    """
    existing_user = await user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    user = await user_crud.create_user(db, user_data)
    return UserRead.model_validate(user)


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_by_admin(
    user_id: int,
    data: PasswordReset_by_admin,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(admin_required)
):
    """
    Admin resets any user's password.
    """
    updated_user = await user_crud.update_password(db, user_id, data.new_password)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return JSONResponse(status_code=200, content={"message": "Password reset successfully."})


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user/admin and returns a JWT access token.
    Note: `username` field is treated as email.
    """
    user = await user_crud.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES ,
        # secure=True,  # Set to True in production with HTTPS
        # samesite="Lax"  # Options: 'Strict', 'Lax', 'None'
    )
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_by_user(
    data: PasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Allows an authenticated user to reset their own password.
    """
    if not verify_password(data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )

    await user_crud.update_password(db, current_user.id, data.new_password)
    return JSONResponse(status_code=200, content={"message": "Password updated successfully."})


@router.get("/all_users", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_all_users_by_admin(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(admin_required)
):
    """
    Admin can retrieve a list of all registered users.
    """
    users = await user_crud.get_all_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No users found.")

    return [UserRead.model_validate(user) for user in users]


@router.delete("/users/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def delete_user_by_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(admin_required)
):
    """
    Admin deletes a user by their ID.
    """
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    await user_crud.delete_user(db, user_id)
    return UserRead.model_validate(user)
