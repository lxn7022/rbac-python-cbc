"""
RBAC 数据模型
Pydantic 模型用于数据验证和序列化
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# 基础模型配置
# ============================================================================

class BaseResponse(BaseModel):
    """基础响应模型"""
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 用户模型
# ============================================================================

class UserBase(BaseModel):
    """用户基础字段"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., max_length=255, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=8, description="密码")


class UserUpdate(BaseModel):
    """更新用户请求"""
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    is_verified: Optional[bool] = Field(None, description="是否验证")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool = True
    is_verified: bool = False
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # 角色列表（可选，用于关联查询）
    roles: Optional[list[dict[str, Any]]] = None


# ============================================================================
# 角色模型
# ============================================================================

class RoleBase(BaseModel):
    """角色基础字段"""
    name: str = Field(..., min_length=2, max_length=50, description="角色名称")
    slug: str = Field(..., min_length=2, max_length=50, description="角色标识")
    description: Optional[str] = Field(None, description="描述")


class RoleCreate(RoleBase):
    """创建角色请求"""
    parent_id: Optional[int] = Field(None, description="父角色 ID")
    priority: int = Field(0, ge=0, description="优先级")
    is_system: bool = Field(False, description="是否系统角色")


class RoleUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, description="描述")
    priority: Optional[int] = Field(None, ge=0, description="优先级")


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    is_system: bool = False
    priority: int = 0
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # 父角色信息（可选）
    parent: Optional[dict[str, Any]] = None
    # 权限列表（可选）
    permissions: Optional[list[dict[str, Any]]] = None


# ============================================================================
# 权限模型
# ============================================================================

class PermissionBase(BaseModel):
    """权限基础字段"""
    resource: str = Field(..., min_length=2, max_length=50, description="资源")
    action: str = Field(..., min_length=2, max_length=50, description="操作")
    description: Optional[str] = Field(None, description="描述")
    module: Optional[str] = Field(None, max_length=50, description="模块")


class PermissionCreate(PermissionBase):
    """创建权限请求"""
    is_system: bool = Field(False, description="是否系统权限")


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int
    is_system: bool = False
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        """返回完整权限名称（如：user:read）"""
        return f"{self.resource}:{self.action}"


# ============================================================================
# 用户角色关联模型
# ============================================================================

class UserRoleBase(BaseModel):
    """用户角色关联基础字段"""
    user_id: int
    role_id: int


class UserRoleCreate(UserRoleBase):
    """创建用户角色关联"""
    assigned_by: Optional[int] = Field(None, description="分配人 ID")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class UserRoleResponse(UserRoleBase):
    """用户角色关联响应"""
    id: int
    assigned_by: Optional[int] = None
    assigned_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    # 关联的角色信息
    roles: Optional[dict[str, Any]] = None


# ============================================================================
# 角色权限关联模型
# ============================================================================

class RolePermissionBase(BaseModel):
    """角色权限关联基础字段"""
    role_id: int
    permission_id: int


class RolePermissionCreate(RolePermissionBase):
    """创建角色权限关联"""
    granted_by: Optional[int] = Field(None, description="授权人 ID")


class RolePermissionResponse(RolePermissionBase):
    """角色权限关联响应"""
    id: int
    granted_by: Optional[int] = None
    granted_at: datetime
    is_active: bool = True
    
    # 关联的权限信息
    permissions: Optional[dict[str, Any]] = None


# ============================================================================
# RBAC 约束模型
# ============================================================================

class RBACConstraintBase(BaseModel):
    """RBAC 约束基础字段"""
    constraint_type: str = Field(..., description="约束类型")
    name: str = Field(..., max_length=100, description="约束名称")
    description: Optional[str] = Field(None, description="描述")
    config: dict[str, Any] = Field(..., description="约束配置")


class RBACConstraintCreate(RBACConstraintBase):
    """创建约束请求"""
    is_active: bool = Field(True, description="是否激活")


class RBACConstraintUpdate(BaseModel):
    """更新约束请求"""
    name: Optional[str] = Field(None, max_length=100, description="约束名称")
    description: Optional[str] = Field(None, description="描述")
    config: Optional[dict[str, Any]] = Field(None, description="约束配置")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RBACConstraintResponse(RBACConstraintBase):
    """约束响应模型"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


# ============================================================================
# 统计模型
# ============================================================================

class UserStats(BaseModel):
    """用户统计"""
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    verified_users: int = Field(..., description="已验证用户数")


class RoleStats(BaseModel):
    """角色统计"""
    total_roles: int = Field(..., description="总角色数")
    system_roles: int = Field(..., description="系统角色数")


class PermissionStats(BaseModel):
    """权限统计"""
    total_permissions: int = Field(..., description="总权限数")
    system_permissions: int = Field(..., description="系统权限数")
    modules: list[str] = Field(default_factory=list, description="模块列表")


# ============================================================================
# 列表响应模型
# ============================================================================

class UserListResponse(BaseModel):
    """用户列表响应"""
    items: list[UserResponse]
    total: int
    page: int
    size: int


class RoleListResponse(BaseModel):
    """角色列表响应"""
    items: list[RoleResponse]
    total: int


class PermissionListResponse(BaseModel):
    """权限列表响应"""
    items: list[PermissionResponse]
    total: int
    page: int
    size: int
