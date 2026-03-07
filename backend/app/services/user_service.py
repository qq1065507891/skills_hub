"""用户服务 - 完整的用户 CRUD 和认证服务"""
from fastapi import HTTPException, status

from app.models.user import User
from app.utils.security import create_access_token, get_password_hash, verify_password


class UserService:
    """用户服务类"""

    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        """根据 ID 获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email):
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip=0, limit=100):
        """获取用户列表"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def register_user(self, user_in):
        """用户注册"""
        if self.get_user_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        if self.get_user_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username, password):
        """用户认证"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def login_user(self, username, password):
        """用户登录"""
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.username})
        return access_token

    def update_user(self, user_id, user_in):
        """更新用户信息"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        update_data = user_in.model_dump(exclude_unset=True)

        if "username" in update_data and update_data["username"] != user.username:
            if self.get_user_by_username(update_data["username"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        if "email" in update_data and update_data["email"] != user.email:
            if self.get_user_by_email(update_data["email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken",
                )

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user_id, password_in):
        """更新用户密码"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not verify_password(password_in.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password",
            )

        user.hashed_password = get_password_hash(password_in.new_password)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id):
        """删除用户"""
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        self.db.delete(user)
        self.db.commit()
        return True
