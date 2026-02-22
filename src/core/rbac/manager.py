"""
RBAC 管理器
提供权限检查、角色管理、权限管理等核心功能
"""

from typing import List, Optional, Dict, Set, Any
from datetime import datetime
from src.db.supabase_client import supabase_db
from src.core.rbac.constraints import ConstraintManager
from src.utils.logger import get_logger
from src.utils.exceptions import (
    RBACError, PermissionDeniedError, RoleNotFoundError,
    ConstraintViolationError, UserNotFoundError
)

logger = get_logger(__name__)


class RBACManager:
    """
    RBAC 管理器
    
    负责：
    1. 权限检查
    2. 角色分配与撤销
    3. 权限授予与撤销
    4. 约束检查
    """
    
    def __init__(self):
        """初始化 RBAC 管理器"""
        self.db = supabase_db
        self.constraint_manager = ConstraintManager(self.db)
    
    # ========================================================================
    # 权限检查方法
    # ========================================================================
    
    def has_permission(
        self,
        user_id: int,
        resource: str,
        action: str,
        check_inheritance: bool = True
    ) -> bool:
        """
        检查用户是否拥有特定权限
        
        Args:
            user_id: 用户ID
            resource: 资源名称（如：user, article）
            action: 操作类型（如：read, write）
            check_inheritance: 是否检查继承的角色权限
        
        Returns:
            bool: 是否拥有权限
        """
        try:
            return self.db.has_permission(user_id, resource, action)
        except Exception as e:
            logger.error(f"检查权限失败: user_id={user_id}, resource={resource}, action={action}, error={e}")
            raise RBACError(f"权限检查失败: {e}")
    
    def has_role(self, user_id: int, role_slug: str) -> bool:
        """
        检查用户是否拥有特定角色
        
        Args:
            user_id: 用户ID
            role_slug: 角色标识符（如：admin, editor）
        
        Returns:
            bool: 是否拥有角色
        """
        try:
            return self.db.has_role(user_id, role_slug)
        except Exception as e:
            logger.error(f"检查角色失败: user_id={user_id}, role_slug={role_slug}, error={e}")
            raise RBACError(f"角色检查失败: {e}")
    
    def get_all_permissions(
        self,
        user_id: int,
        include_inherited: bool = True
    ) -> Set[str]:
        """
        获取用户所有权限
        
        Args:
            user_id: 用户ID
            include_inherited: 是否包含继承的角色权限
        
        Returns:
            Set[str]: 权限集合（格式：resource:action）
        """
        try:
            permissions = self.db.get_user_permissions(user_id)
            return {f"{p['resource']}:{p['action']}" for p in permissions}
        except Exception as e:
            logger.error(f"获取用户权限失败: user_id={user_id}, error={e}")
            raise RBACError(f"获取权限失败: {e}")
    
    def check_multiple_permissions(
        self,
        user_id: int,
        permissions: List[tuple]
    ) -> Dict[str, bool]:
        """
        批量检查权限
        
        Args:
            user_id: 用户ID
            permissions: 权限列表 [(resource, action), ...]
        
        Returns:
            Dict[str, bool]: 权限检查结果
        """
        try:
            user_permissions = self.get_all_permissions(user_id)
            
            result = {}
            for resource, action in permissions:
                permission_key = f"{resource}:{action}"
                result[permission_key] = permission_key in user_permissions
            
            return result
        except Exception as e:
            logger.error(f"批量检查权限失败: user_id={user_id}, error={e}")
            raise RBACError(f"批量检查权限失败: {e}")
    
    # ========================================================================
    # 角色管理方法
    # ========================================================================
    
    def assign_role(
        self,
        user_id: int,
        role_id: int,
        assigned_by: Optional[int] = None,
        expires_at: Optional[datetime] = None
    ) -> dict[str, Any]:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            assigned_by: 分配人ID
            expires_at: 过期时间（可选）
        
        Returns:
            dict: 用户角色关联记录
        
        Raises:
            ConstraintViolationError: 违反约束规则
        """
        try:
            # 1. 检查约束规则
            self.constraint_manager.check_constraints(
                user_id=user_id,
                role_id=role_id,
                action='assign'
            )
            
            # 2. 检查是否已存在
            existing = self.db.get_user_role_by_id(user_id, role_id)
            
            if existing:
                # 如果已存在但不活跃，重新激活
                if not existing.get("is_active"):
                    # 更新为活跃状态
                    expires_str = expires_at.isoformat() if expires_at else None
                    result = self.db.assign_role(user_id, role_id, assigned_by, expires_str)
                    logger.info(f"重新激活角色: user_id={user_id}, role_id={role_id}")
                    return result
                else:
                    logger.warning(f"用户已拥有该角色: user_id={user_id}, role_id={role_id}")
                    return existing
            
            # 3. 创建新的关联
            expires_str = expires_at.isoformat() if expires_at else None
            result = self.db.assign_role(user_id, role_id, assigned_by, expires_str)
            
            logger.info(f"分配角色成功: user_id={user_id}, role_id={role_id}")
            return result
            
        except ConstraintViolationError:
            raise
        except Exception as e:
            logger.error(f"分配角色失败: user_id={user_id}, role_id={role_id}, error={e}")
            raise RBACError(f"分配角色失败: {e}")
    
    def revoke_role(self, user_id: int, role_id: int) -> bool:
        """
        撤销用户的角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
        
        Returns:
            bool: 是否成功撤销
        """
        try:
            success = self.db.revoke_role(user_id, role_id)
            
            if success:
                logger.info(f"撤销角色成功: user_id={user_id}, role_id={role_id}")
            else:
                logger.warning(f"未找到用户角色关联: user_id={user_id}, role_id={role_id}")
            
            return success
        except Exception as e:
            logger.error(f"撤销角色失败: user_id={user_id}, role_id={role_id}, error={e}")
            raise RBACError(f"撤销角色失败: {e}")
    
    def get_user_roles(self, user_id: int) -> List[dict[str, Any]]:
        """
        获取用户的所有角色
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[dict]: 角色列表
        """
        try:
            user_roles = self.db.get_user_roles(user_id)
            # 提取角色信息
            return [ur.get("roles") for ur in user_roles if ur.get("roles")]
        except Exception as e:
            logger.error(f"获取用户角色失败: user_id={user_id}, error={e}")
            raise RBACError(f"获取角色失败: {e}")
    
    # ========================================================================
    # 权限管理方法
    # ========================================================================
    
    def grant_permission(
        self,
        role_id: int,
        permission_id: int,
        granted_by: Optional[int] = None
    ) -> dict[str, Any]:
        """
        为角色授予权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
            granted_by: 授权人ID
        
        Returns:
            dict: 角色权限关联记录
        """
        try:
            # 检查是否已存在
            existing = self.db.get_role_permission_by_id(role_id, permission_id)
            
            if existing:
                if not existing.get("is_active"):
                    # 重新激活
                    result = self.db.grant_permission(role_id, permission_id, granted_by)
                    logger.info(f"重新激活权限: role_id={role_id}, permission_id={permission_id}")
                    return result
                else:
                    logger.warning(f"角色已拥有该权限: role_id={role_id}, permission_id={permission_id}")
                    return existing
            
            # 创建新的关联
            result = self.db.grant_permission(role_id, permission_id, granted_by)
            
            logger.info(f"授予权限成功: role_id={role_id}, permission_id={permission_id}")
            return result
        except Exception as e:
            logger.error(f"授予权限失败: role_id={role_id}, permission_id={permission_id}, error={e}")
            raise RBACError(f"授予权限失败: {e}")
    
    def revoke_permission(self, role_id: int, permission_id: int) -> bool:
        """
        撤销角色的权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
        
        Returns:
            bool: 是否成功撤销
        """
        try:
            success = self.db.revoke_permission(role_id, permission_id)
            
            if success:
                logger.info(f"撤销权限成功: role_id={role_id}, permission_id={permission_id}")
            else:
                logger.warning(f"未找到角色权限关联: role_id={role_id}, permission_id={permission_id}")
            
            return success
        except Exception as e:
            logger.error(f"撤销权限失败: role_id={role_id}, permission_id={permission_id}, error={e}")
            raise RBACError(f"撤销权限失败: {e}")
    
    def get_role_permissions(self, role_id: int) -> List[dict[str, Any]]:
        """
        获取角色的所有权限
        
        Args:
            role_id: 角色ID
        
        Returns:
            List[dict]: 权限列表
        """
        try:
            role_permissions = self.db.get_role_permissions(role_id)
            # 提取权限信息
            return [rp.get("permissions") for rp in role_permissions if rp.get("permissions")]
        except Exception as e:
            logger.error(f"获取角色权限失败: role_id={role_id}, error={e}")
            raise RBACError(f"获取权限失败: {e}")
    
    # ========================================================================
    # 辅助方法
    # ========================================================================
    
    def get_user_with_roles(self, user_id: int) -> Optional[dict[str, Any]]:
        """
        获取用户及其角色信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            dict: 用户信息（包含角色列表）
        """
        try:
            user = self.db.get_user_by_id(user_id)
            if not user:
                return None
            
            # 获取用户角色
            roles = self.get_user_roles(user_id)
            user["roles"] = roles
            
            return user
        except Exception as e:
            logger.error(f"获取用户信息失败: user_id={user_id}, error={e}")
            raise RBACError(f"获取用户信息失败: {e}")
    
    def get_role_with_permissions(self, role_id: int) -> Optional[dict[str, Any]]:
        """
        获取角色及其权限信息
        
        Args:
            role_id: 角色ID
        
        Returns:
            dict: 角色信息（包含权限列表）
        """
        try:
            role = self.db.get_role_by_id(role_id)
            if not role:
                return None
            
            # 获取角色权限
            permissions = self.get_role_permissions(role_id)
            role["permissions"] = permissions
            
            return role
        except Exception as e:
            logger.error(f"获取角色信息失败: role_id={role_id}, error={e}")
            raise RBACError(f"获取角色信息失败: {e}")


# 全局 RBAC 管理器实例
rbac_manager = RBACManager()
