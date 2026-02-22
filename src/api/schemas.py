"""
API 数据模型
使用 Pydantic 定义请求和响应模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# 用户相关
# ============================================================================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """用户创建请求"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """用户更新请求"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserResponse]
    total: int
    page: int
    size: int


# ============================================================================
# 角色相关
# ============================================================================

class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., min_length=2, max_length=50)
    slug: str = Field(..., min_length=2, max_length=50, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None
    priority: int = Field(default=0, ge=0)


class RoleCreate(RoleBase):
    """角色创建请求"""
    parent_id: Optional[int] = None


class RoleUpdate(BaseModel):
    """角色更新请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = None


class RoleResponse(RoleBase):
    """角色响应"""
    id: int
    is_system: bool
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """角色列表响应"""
    items: List[RoleResponse]
    total: int


# ============================================================================
# 权限相关
# ============================================================================

class PermissionBase(BaseModel):
    """权限基础模型"""
    resource: str = Field(..., min_length=2, max_length=50)
    action: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    module: Optional[str] = Field(None, max_length=50)


class PermissionCreate(PermissionBase):
    """权限创建请求"""
    pass


class PermissionResponse(PermissionBase):
    """权限响应"""
    id: int
    is_system: bool
    full_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """权限列表响应"""
    items: List[PermissionResponse]
    total: int


# ============================================================================
# 认证相关
# ============================================================================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RegisterRequest(UserCreate):
    """注册请求"""
    pass


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# 角色分配相关
# ============================================================================

class AssignRoleRequest(BaseModel):
    """分配角色请求"""
    role_id: int
    expires_at: Optional[datetime] = None


class GrantPermissionRequest(BaseModel):
    """授予权限请求"""
    permission_id: int


# ============================================================================
# 通用响应
# ============================================================================

class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    error_code: Optional[str] = None


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleListResponse",
    "PermissionBase",
    "PermissionCreate",
    "PermissionResponse",
    "PermissionListResponse",
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "TokenResponse",
    "AssignRoleRequest",
    "GrantPermissionRequest",
    "MessageResponse",
    "ErrorResponse",
]
