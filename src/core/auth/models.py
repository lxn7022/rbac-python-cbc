"""
认证相关模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token 模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """Token 载荷"""
    sub: int  # user_id
    username: str
    email: str
    exp: datetime
    iat: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp()
        }


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserCreate(BaseModel):
    """用户创建请求"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


__all__ = [
    "Token",
    "TokenPayload",
    "LoginRequest",
    "LoginResponse",
    "UserCreate",
    "UserResponse",
]
