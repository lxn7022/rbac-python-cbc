"""
权限定义和常量
预定义系统权限，便于代码中引用
"""

from enum import Enum
from typing import List, Dict


# ============================================================================
# 权限枚举
# ============================================================================

class Resource(Enum):
    """资源枚举"""
    USER = 'user'
    ROLE = 'role'
    PERMISSION = 'permission'
    ARTICLE = 'article'
    ORDER = 'order'
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有资源"""
        return [item.value for item in cls]


class Action(Enum):
    """操作枚举"""
    READ = 'read'
    WRITE = 'write'
    CREATE = 'create'
    DELETE = 'delete'
    MANAGE = 'manage'
    ASSIGN = 'assign'
    REVOKE = 'revoke'
    PUBLISH = 'publish'
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有操作"""
        return [item.value for item in cls]


class Module(Enum):
    """模块枚举"""
    AUTH = 'auth'
    RBAC = 'rbac'
    CONTENT = 'content'
    ORDER = 'order'
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有模块"""
        return [item.value for item in cls]


# ============================================================================
# 权限常量类
# ============================================================================

class Permission:
    """
    权限常量类
    
    使用示例：
        Permission.USER_READ
        Permission.ARTICLE_WRITE
    """
    
    # 用户相关权限
    USER_READ = 'user:read'
    USER_WRITE = 'user:write'
    USER_CREATE = 'user:create'
    USER_DELETE = 'user:delete'
    USER_MANAGE = 'user:manage'
    
    # 角色相关权限
    ROLE_READ = 'role:read'
    ROLE_WRITE = 'role:write'
    ROLE_CREATE = 'role:create'
    ROLE_DELETE = 'role:delete'
    ROLE_MANAGE = 'role:manage'
    
    # 权限相关权限
    PERMISSION_READ = 'permission:read'
    PERMISSION_ASSIGN = 'permission:assign'
    PERMISSION_REVOKE = 'permission:revoke'
    
    # 文章相关权限
    ARTICLE_READ = 'article:read'
    ARTICLE_WRITE = 'article:write'
    ARTICLE_DELETE = 'article:delete'
    ARTICLE_PUBLISH = 'article:publish'
    
    # 订单相关权限
    ORDER_READ = 'order:read'
    ORDER_WRITE = 'order:write'
    ORDER_DELETE = 'order:delete'
    ORDER_MANAGE = 'order:manage'


# ============================================================================
# 角色常量类
# ============================================================================

class Role:
    """
    角色常量类
    
    使用示例：
        Role.SUPER_ADMIN
        Role.ADMIN
    """
    
    SUPER_ADMIN = 'super-admin'
    ADMIN = 'admin'
    EDITOR = 'editor'
    USER = 'user'
    GUEST = 'guest'


# ============================================================================
# 权限分组定义
# ============================================================================

PERMISSION_GROUPS: Dict[str, List[str]] = {
    '用户管理': [
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_CREATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE,
    ],
    '角色管理': [
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_CREATE,
        Permission.ROLE_DELETE,
        Permission.ROLE_MANAGE,
    ],
    '权限管理': [
        Permission.PERMISSION_READ,
        Permission.PERMISSION_ASSIGN,
        Permission.PERMISSION_REVOKE,
    ],
    '内容管理': [
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
    ],
    '订单管理': [
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ORDER_MANAGE,
    ],
}


# ============================================================================
# 默认角色权限映射
# ============================================================================

DEFAULT_ROLE_PERMISSIONS: Dict[str, List[str]] = {
    Role.SUPER_ADMIN: [
        # 超级管理员拥有所有权限
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_CREATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE,
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_CREATE,
        Permission.ROLE_DELETE,
        Permission.ROLE_MANAGE,
        Permission.PERMISSION_READ,
        Permission.PERMISSION_ASSIGN,
        Permission.PERMISSION_REVOKE,
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ORDER_MANAGE,
    ],
    Role.ADMIN: [
        # 管理员（无删除用户和角色权限）
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_CREATE,
        Permission.USER_MANAGE,
        Permission.ROLE_READ,
        Permission.ROLE_WRITE,
        Permission.ROLE_CREATE,
        Permission.ROLE_MANAGE,
        Permission.PERMISSION_READ,
        Permission.PERMISSION_ASSIGN,
        Permission.PERMISSION_REVOKE,
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
        Permission.ORDER_READ,
        Permission.ORDER_WRITE,
        Permission.ORDER_DELETE,
        Permission.ORDER_MANAGE,
    ],
    Role.EDITOR: [
        # 编辑（内容管理权限）
        Permission.USER_READ,
        Permission.ARTICLE_READ,
        Permission.ARTICLE_WRITE,
        Permission.ARTICLE_DELETE,
        Permission.ARTICLE_PUBLISH,
    ],
    Role.USER: [
        # 普通用户（基础读取权限）
        Permission.ARTICLE_READ,
        Permission.ORDER_READ,
    ],
    Role.GUEST: [
        # 访客（无权限）
    ],
}


# ============================================================================
# 辅助函数
# ============================================================================

def parse_permission(permission_str: str) -> tuple:
    """
    解析权限字符串
    
    Args:
        permission_str: 权限字符串（如：'user:read'）
    
    Returns:
        tuple: (resource, action)
    
    Example:
        >>> parse_permission('user:read')
        ('user', 'read')
    """
    parts = permission_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"无效的权限格式: {permission_str}")
    return parts[0], parts[1]


def format_permission(resource: str, action: str) -> str:
    """
    格式化权限字符串
    
    Args:
        resource: 资源名称
        action: 操作类型
    
    Returns:
        str: 权限字符串
    
    Example:
        >>> format_permission('user', 'read')
        'user:read'
    """
    return f"{resource}:{action}"


__all__ = [
    "Resource",
    "Action",
    "Module",
    "Permission",
    "Role",
    "PERMISSION_GROUPS",
    "DEFAULT_ROLE_PERMISSIONS",
    "parse_permission",
    "format_permission",
]
