"""认证依赖 - JWT 认证"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

# 使用 auto_error=False 使其在缺少 token 时不自动抛出 403 错误
security = HTTPBearer(auto_error=False)


async def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """从请求中获取 Token"""
    if credentials is None:
        return None
    return credentials.credentials


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(get_token),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户（必需）"""
    # 如果没有从 HTTPBearer 获取到 token，尝试从 header 直接获取
    if token is None:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(get_token),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前认证用户（可选，未认证返回 None）"""
    # 如果没有从 HTTPBearer 获取到 token，尝试从 header 直接获取
    if token is None:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

    if token is None:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    username = payload.get("sub")
    if username is None:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前激活用户"""
    return current_user
