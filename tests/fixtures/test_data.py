"""
测试数据 fixtures
使用 Supabase REST API 提供测试数据
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from src.db.supabase_client import supabase_db
from src.core.auth.models import UserCreate
from src.core.auth.services import auth_service


def create_test_user(
    username: str = None,
    email: str = None,
    password: str = "testpass123",
    full_name: str = "测试用户"
) -> Dict[str, Any]:
    """
    创建测试用户
    
    Args:
        username: 用户名（自动生成如果未提供）
        email: 邮箱（自动生成如果未提供）
        password: 密码
        full_name: 全名
    
    Returns:
        Dict: 创建的用户数据
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    username = username or f"test_user_{timestamp}"
    email = email or f"{username}@test.com"
    
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        full_name=full_name
    )
    
    return auth_service.create_user(user_data)


def create_test_role(
    name: str = None,
    slug: str = None,
    priority: int = 50,
    parent_id: int = None
) -> Dict[str, Any]:
    """
    创建测试角色
    
    Args:
        name: 角色名称（自动生成如果未提供）
        slug: 角色标识（自动生成如果未提供）
        priority: 优先级
        parent_id: 父角色 ID
    
    Returns:
        Dict: 创建的角色数据
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    name = name or f"测试角色_{timestamp}"
    slug = slug or f"test-role-{timestamp}"
    
    role_data = {
        "name": name,
        "slug": slug,
        "description": f"测试角色 - {name}",
        "priority": priority,
        "parent_id": parent_id,
        "is_system": False
    }
    
    return supabase_db.create_role(role_data)


def create_test_permission(
    resource: str = None,
    action: str = None,
    description: str = "测试权限",
    module: str = "test"
) -> Dict[str, Any]:
    """
    创建测试权限
    
    Args:
        resource: 资源名称（自动生成如果未提供）
        action: 操作类型（自动生成如果未提供）
        description: 描述
        module: 所属模块
    
    Returns:
        Dict: 创建的权限数据
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    resource = resource or f"test_resource_{timestamp}"
    action = action or f"test_action_{timestamp}"
    
    permission_data = {
        "resource": resource,
        "action": action,
        "description": description,
        "module": module,
        "is_system": False
    }
    
    return supabase_db.create_permission(permission_data)


def assign_role_to_user(
    user_id: int,
    role_id: int,
    expires_at: datetime = None
) -> Dict[str, Any]:
    """
    为用户分配角色
    
    Args:
        user_id: 用户 ID
        role_id: 角色 ID
        expires_at: 过期时间
    
    Returns:
        Dict: 用户角色关联数据
    """
    return supabase_db.assign_role_to_user(
        user_id=user_id,
        role_id=role_id,
        expires_at=expires_at
    )


def grant_permission_to_role(
    role_id: int,
    permission_id: int
) -> Dict[str, Any]:
    """
    为角色授予权限
    
    Args:
        role_id: 角色 ID
        permission_id: 权限 ID
    
    Returns:
        Dict: 角色权限关联数据
    """
    return supabase_db.grant_permission_to_role(role_id, permission_id)


def create_full_user_with_permissions(
    username: str = None,
    role_name: str = None,
    permissions: List[str] = None
) -> Dict[str, Any]:
    """
    创建完整用户，包含角色和权限
    
    Args:
        username: 用户名（自动生成如果未提供）
        role_name: 角色名称（自动生成如果未提供）
        permissions: 权限列表（格式：["resource:action"]）
    
    Returns:
        Dict: 包含用户、角色、权限的字典
    """
    # 创建用户
    user = create_test_user(username=username)
    
    # 创建角色
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    role_name = role_name or f"测试角色_{timestamp}"
    role = create_test_role(name=role_name, slug=f"test-role-{timestamp}")
    
    # 创建权限并分配给角色
    if permissions is None:
        permissions = ["test:read", "test:write"]
    
    for perm_str in permissions:
        resource, action = perm_str.split(":")
        permission = create_test_permission(resource=resource, action=action)
        grant_permission_to_role(role["id"], permission["id"])
    
    # 分配角色给用户
    assign_role_to_user(user["id"], role["id"])
    
    return {
        "user": user,
        "role": role,
        "permissions": permissions
    }


def create_role_hierarchy(
    levels: int = 3
) -> List[Dict[str, Any]]:
    """
    创建角色层级
    
    Args:
        levels: 层级数
    
    Returns:
        List[Dict]: 创建的角色列表
    """
    roles = []
    parent_id = None
    
    for i in range(levels):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        role = create_test_role(
            name=f"角色{i + 1}_{timestamp}",
            slug=f"role-{i + 1}-{timestamp}",
            priority=100 - i * 20,
            parent_id=parent_id
        )
        roles.append(role)
        parent_id = role["id"]
    
    return roles


def cleanup_test_data():
    """
    清理测试数据
    
    注意：Supabase REST API 不直接支持批量删除
    建议在测试后手动清理或使用数据库触发器
    """
    pass
