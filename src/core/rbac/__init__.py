"""RBAC 核心模块"""

# 数据模型（Pydantic）
from .models import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    RoleBase, RoleCreate, RoleUpdate, RoleResponse,
    PermissionBase, PermissionCreate, PermissionResponse,
    UserRoleBase, UserRoleCreate, UserRoleResponse,
    RolePermissionBase, RolePermissionCreate, RolePermissionResponse,
    RBACConstraintBase, RBACConstraintCreate, RBACConstraintUpdate, RBACConstraintResponse,
    UserStats, RoleStats, PermissionStats,
    UserListResponse, RoleListResponse, PermissionListResponse,
)

# 管理器
from .manager import RBACManager, rbac_manager

# 权限常量
from .permissions import Permission as PermissionConst, Role as RoleConst

# 约束
from .constraints import ConstraintManager

# 为了向后兼容，创建简短别名
User = UserResponse
Role = RoleResponse
Permission = PermissionResponse
UserRole = UserRoleResponse
RolePermission = RolePermissionResponse
RBACConstraint = RBACConstraintResponse

__all__ = [
    # 基础模型
    "UserBase", "UserCreate", "UserUpdate", "User",
    "RoleBase", "RoleCreate", "RoleUpdate", "Role",
    "PermissionBase", "PermissionCreate", "Permission",
    "UserRoleBase", "UserRoleCreate", "UserRole",
    "RolePermissionBase", "RolePermissionCreate", "RolePermission",
    "RBACConstraintBase", "RBACConstraintCreate", "RBACConstraintUpdate", "RBACConstraint",
    
    # 统计模型
    "UserStats", "RoleStats", "PermissionStats",
    
    # 列表响应
    "UserListResponse", "RoleListResponse", "PermissionListResponse",
    
    # 管理器和常量
    "RBACManager", "rbac_manager",
    "ConstraintManager",
    "PermissionConst", "RoleConst",
]
