"""
用户相关 API
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.user import (
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
    UserUpdatePassword,
)
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    service = UserService(db)
    return service.register_user(user_in)


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """用户登录，返回 JWT Token"""
    service = UserService(db)
    access_token = service.login_user(user_in.username, user_in.password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户信息"""
    return current_user


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """获取用户列表"""
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """获取单个用户"""
    service = UserService(db)
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新用户信息（只能更新自己）"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )
    service = UserService(db)
    return service.update_user(user_id, user_in)


@router.put("/{user_id}/password", response_model=UserResponse)
def update_user_password(
    user_id: int,
    password_in: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新用户密码（只能更新自己）"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's password",
        )
    service = UserService(db)
    return service.update_password(user_id, password_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除用户（只能删除自己）"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )
    service = UserService(db)
    service.delete_user(user_id)
